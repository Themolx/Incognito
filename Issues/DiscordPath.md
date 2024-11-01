# Zpětné lomítko v Discord zprávách

## Problém
Discord automaticky odstraňuje zpětné lomítko (`\`) pokud je umístěno před podtržítkem (`_`). Toto chování způsobuje problémy při sdílení cest k souborům v týmové komunikaci.

### Příklad problematické cesty
```
P:\EPET3D_02413\sources\_client_to\240828_previews
```

## Řešení
Použijte zpětné apostrofy (backticks) kolem celé cesty:
```
`P:\EPET3D_02413\sources\_client_to\240828_previews`
```

## Jak napsat backtick (`)

### Backtick na různých klávesnicích
- **Česká klávesnice**: Zpětný apostrof je pod klávesou Esc
- **Anglická klávesnice**: Pod klávesou Esc (vlevo nahoře)

### Zpětné lomítko (\)
- **Česká klávesnice**: `Shift + klávesa vlevo od Enter`
- **Anglická klávesnice**: Klávesa vlevo od Enter

Pro více řádků použijte trojité backticks:
````
```
P:\EPET3D_02413\sources\_client_to\240828_previews
P:\EPET3D_02413\sources\_client_to\another_path
```
````
