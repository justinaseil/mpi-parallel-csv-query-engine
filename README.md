# MPI CSV GroupBy

Sukurta universali MPI pagrįsta sistema, skirta vykdyti SQL tipo agregavimo užklausas labai didelės apimties CSV duomenų rinkiniams, nepriklausomai nuo jų struktūros. Sistema efektyviai paskirsto duomenų apdorojimą tarp procesų ir sumažina duomenų perdavimo apimtį.

## Duomenys
Real Estate Sales 2001–2023 (Data.gov), >1 mln. eilučių. Žr. `data/README.md`.

## Algoritmo schema
1. Paskirstytojas:
• Perskaito vartotojo užklausą ir CSV failą blokais.
• Išsiunčia užklausą visiems darbininkams (bcast).

2. Darbininkai:
• Gavę užklausą, laukia CSV duomenų bloko iš paskirstytojo.
• Gavę duomenų bloką, taiko WHERE filtravimą.
• Jei rezultatas ne tuščias, atlieka grupavimą ir agregaciją.
• Siunčia dalinį rezultatą atgal paskirstytojo procesui.

3. Paskirstytojas:
• Surenka dalinius rezultatus iš darbininkų.
• Jei yra likusių CSV duomenų blokų, siunčia naują darbą atitinkamam darbininkui.
• Kai visi duomenų blokai apdoroti, sujungia visus dalinius rezultatus.
• Atlieka galutinį grupavimą ir agregaciją.
• Spausdina galutinį rezultatą ir vykdymo laiką.

## Paleidimo instrukcijos
Sistema paleidžiama naudojant mpirun. Pavyzdžiai:
```bash
mpirun -n 2 python main_mpi.py --input data.csv --where "Town==Ansonia" --
group-by "Property_Type" --agg "Sale_Amount=count"
mpirun -n 4 python main_mpi.py --input data.csv --where "Town==Ansonia" --
group-by "Property_Type" --agg "Sale_Amount=count"
mpirun -n 7 python main_mpi.py --input data.csv --where "Town==Ansonia" --
group-by "Property_Type" --agg "Sale_Amount=count"
```
Pastaba:
• -n <procesų skaičius> nurodo darbininkų procesų skaičių + 1 paskirstytoją.
• --where – filtravimo sąlyga.
• --group-by – stulpelis, pagal kurį grupuojame.
• --agg – agregavimo funkcija (pvz. sum, mean, count).

## Rezultatų teisingumas

Rezultatai parodė, kad nepriklausomai nuo to, kiek procesų naudojame (2, 4 ar 7), galutinis rezultatas vis tiek yra tas pats, o tai reiškia, kad duomenų dalinimas ir surinkimas veikia teisingai.

## Scaling rezultatai

| Procesai | Laikas (s) | Greitėjimas | Efektyvumas |
|---|---|---|---|
| 2 | 2,6145 | 1,00 | 0,5 |
| 4 | 2,1656 | 1,21 | 0,3 |
| 7 | 2,2266 | 1,17 | 0,17 |

Didinant procesų skaičių programa veikia greičiau, bet efektyvumas mažėja.
