
### **Problém: Discord Automaticky Odstraňuje "\" Pokud Je Před Ní "_”**

**Popis problému:**
Při vkládání cest k souborům do Discordu bylo zjištěno, že Discord automaticky odstraní znak "\" (zpětné lomítko), pokud je umístěno před podtržítkem "_". To může vést k nesprávnému zobrazení cest, což způsobuje zmatky nebo potenciální chyby při komunikaci ohledně cest k souborům.

**Kroky k reprodukci:**
1. Vložte cestu k souboru do Discordu ve formátu `P:\EPET3D_02413\sources\_client_to\240828_previews`.
2. Všimněte si, že Discord automaticky odstraní "\" po podtržítku "_".

**Očekávané chování:**
Cesta k souboru by měla být zobrazena správně, s ponechanými "\" jako v původním vloženém textu.

**Příčina:**
Jde o chování v parseru Discordu, který interpretuje "\" následované "_" jako escape sekvenci nebo jednoduše odstraní zpětné lomítko, čímž naruší formátování zamýšlené cesty.

**Řešení:**
Při vkládání do Discordu obalte cestu do trojitých zpětných apostrofů nebo do jednoduchých uvozovek. Tím zabráníte Discordu v modifikaci "\" a zajistíte správné zobrazení cesty.

**Příklad řešení:**
Použijte následující formát:
\```
`P:\EPET3D_02413\sources\_client_to\240828_previews`
\```
nebo
\```
\```
P:\EPET3D_02413\sources\_client_to\240828_previews
\```
\```

Tato metoda zaručuje, že cesta zůstane neporušená a bude jasně komunikována ostatním členům týmu na Discordu.
