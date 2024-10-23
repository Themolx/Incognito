
### **Problém: Spuštění AE Render Engine místo plné verze After Effects**

**Popis problému:**
Při spuštění After Effects se místo plné verze aplikace spustí pouze AE Render Engine. Tento problém způsobuje omezenou funkčnost, protože AE Render Engine slouží jen k renderování a neposkytuje přístup ke všem funkcím After Effects.

**Kroky k reprodukci:**
1. Otevřete After Effects pomocí zástupce nebo ikony aplikace.
2. Zjistíte, že se spustí AE Render Engine místo plné verze After Effects.

**Očekávané chování:**
Po spuštění by se měla otevřít plná verze After Effects s kompletními editačními nástroji a funkcemi.

**Příčina:**
Tento problém je způsoben přítomností souboru `ae_render_only_node.txt`, který After Effects identifikuje jako signál k otevření pouze Render Engine.

**Řešení:**
Smažte soubor `ae_render_only_node.txt`, který se nachází ve složce:
```
C:\Users\YourUser\Documents\
```
Tímto krokem se obnoví správné spuštění plné verze After Effects.
