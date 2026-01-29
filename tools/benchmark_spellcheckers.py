import time
import os
import psutil
from contextlib import contextmanager

def get_memory_mb():
    """Retourne la mémoire utilisée en Mo"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

@contextmanager
def timer(name):
    start = time.perf_counter()
    yield
    print(f"  ⏱️  {name}: {time.perf_counter() - start:.2f}s")

class SpellCheckerComparator:
    def __init__(self, load_languagetool=True):
        self.tools = {}
        print(f"Base Memory: {get_memory_mb():.1f} Mo")
        
        # PySpellChecker (léger)
        try:
            with timer("pyspellchecker"):
                from spellchecker import SpellChecker
                self.tools['pyspellchecker'] = SpellChecker(language='fr')
                print(f"  +Mem: {get_memory_mb():.1f} Mo")
        except ImportError:
            print("  ⚠️  Pyspellchecker non installé.")
            
        # Hunspell (léger)
        try:
            with timer("hunspell"):
                import hunspell
                # Try common paths for Mac/Linux
                dic_paths = [
                    ('/Library/Spelling/fr_FR.dic', '/Library/Spelling/fr_FR.aff'),
                    ('/usr/share/hunspell/fr_FR', '/usr/share/hunspell/fr_FR'), # prefix style
                    ('/usr/share/hunspell/fr_FR.dic', '/usr/share/hunspell/fr_FR.aff'),
                ]
                
                hobj = None
                for d, a in dic_paths:
                    if os.path.exists(d) and os.path.exists(a):
                        hobj = hunspell.HunSpell(d, a)
                        break
                    # Handle prefix case
                    if os.path.exists(d + '.dic') and os.path.exists(d + '.aff'):
                         hobj = hunspell.HunSpell(d + '.dic', d + '.aff')
                         break
                         
                if hobj:
                    self.tools['hunspell'] = hobj
                    print(f"  +Mem: {get_memory_mb():.1f} Mo")
                else:
                    print("  ⚠️  Dictionnaires Hunspell introuvables.")
        except ImportError:
            print("  ⚠️  Hunspell non installé.")
        except Exception as e:
            print(f"  ⚠️  Hunspell erreur: {e}")
        
        # LanguageTool (lourd - optionnel)
        if load_languagetool:
            try:
                with timer("language-tool"):
                    import language_tool_python
                    self.tools['languagetool'] = language_tool_python.LanguageTool('fr')
                    print(f"  +Mem: {get_memory_mb():.1f} Mo")
            except ImportError:
                print("  ⚠️  LanguageTool non installé.")
            except Exception as e:
                print(f"  ⚠️  LanguageTool non disponible: {e}")
    
    def check_word(self, word):
        """Compare la vérification d'un mot"""
        results = {}
        
        if 'pyspellchecker' in self.tools:
            tool = self.tools['pyspellchecker']
            start = time.perf_counter()
            is_correct = word in tool
            suggestions = list(tool.candidates(word) or [])[:5]
            dt = time.perf_counter() - start
            results['pyspellchecker'] = {
                'correct': is_correct,
                'suggestions': suggestions,
                'time': dt
            }
        
        if 'hunspell' in self.tools:
            tool = self.tools['hunspell']
            start = time.perf_counter()
            is_correct = tool.spell(word)
            suggestions = tool.suggest(word)[:5] if not is_correct else []
            dt = time.perf_counter() - start
            results['hunspell'] = {
                'correct': is_correct,
                'suggestions': suggestions,
                'time': dt
            }
        
        if 'languagetool' in self.tools:
            tool = self.tools['languagetool']
            start = time.perf_counter()
            matches = tool.check(word)
            is_correct = len(matches) == 0
            suggestions = matches[0].replacements[:5] if matches else []
            dt = time.perf_counter() - start
            results['languagetool'] = {
                'correct': is_correct,
                'suggestions': suggestions,
                'time': dt
            }
        
        return results
    
    def close(self):
        """Libère la mémoire"""
        if 'languagetool' in self.tools:
            self.tools['languagetool'].close()

if __name__ == "__main__":
    print("🔄 Chargement des outils...\n")
    # On essaie tout
    comparator = SpellCheckerComparator(load_languagetool=True)
    
    print("\n" + "="*50)
    print("📝 Test sur un mot : 'bonjoure'\n")
    
    test_word = "bonjoure"
    results = comparator.check_word(test_word)
    
    for tool_name, result in results.items():
        print(f"{tool_name}:")
        print(f"  Correct: {result['correct']}")
        print(f"  Time: {result['time']:.6f}s")
        print()
    
    print("="*50)
    print("📝 Test sur un mot difficule : 'anti-constitutionnellement'\n")
    results = comparator.check_word("anticonstitutionnellement")
    for tool_name, result in results.items():
        print(f"{tool_name}: {result['correct']} ({result['time']:.6f}s)")

    comparator.close()
