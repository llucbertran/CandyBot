> **Nota:** Aquesta carpeta conté prototips inicials de visió per computador. No
> formen part del sistema final, que utilitza `BotSoftware/VC/color_centre.py` i
> `camera_stream.py`. Es conserven com a documentació de la investigació.

# Detecció de color de Skittles amb Visió per Computador

Aquest directori conté un petit programa en Python per detectar automàticament el color d'un Skittle a partir d'imatges capturades amb càmera.

El codi utilitza **OpenCV** i **NumPy** per processar les imatges, localitzar l'objecte principal i classificar el seu color mitjançant l'espai de color **HSV**.

---

## Objectiu

L'objectiu és provar una primera versió del sistema de visió per computador que més endavant es podria executar en una Raspberry Pi amb càmera.

En aquesta prova, no s'utilitza encara la Raspberry Pi. Les imatges ja estan capturades prèviament i el programa les analitza des d'un ordinador.

El sistema:

1. Llegeix totes les imatges d'una carpeta.
2. Detecta l'objecte circular que correspon al Skittle.
3. Calcula el color dominant del Skittle.
4. Classifica el color.
5. Mostra la imatge amb la detecció marcada.
6. Imprimeix un resum final amb el color detectat per cada imatge.

---

## Fitxers

Exemple d'estructura de la carpeta:

```txt
VC/
├── detectar_colors.py
├── prova1.jpg
├── prova2.jpg
├── prova3.jpg
├── prova4.jpg
├── prova5.jpg
├── prova6.jpg
└── README.md
```

Les imatges de prova són:

```txt
prova1.jpg
prova2.jpg
prova3.jpg
prova4.jpg
prova5.jpg
prova6.jpg
```

Cada imatge conté un Skittle d'un color diferent.

---

## Requisits

Cal tenir instal·lat Python i les llibreries següents:

```bash
pip install opencv-python numpy
```

Si `pip` no funciona directament, es pot provar:

```bash
py -m pip install opencv-python numpy
```

---

## Execució

Des de la carpeta on es troben les imatges i el fitxer `detectar_colors.py`, executar:

```bash
python detectar_colors.py
```

o bé:

```bash
py detectar_colors.py
```

---

## Funcionament general del codi

El programa segueix aquest procés:

```txt
Llegir imatge
↓
Convertir imatge de BGR a HSV
↓
Crear una màscara de zones amb color viu
↓
Buscar contorns
↓
Seleccionar el contorn que més sembla un Skittle
↓
Calcular el color dominant
↓
Classificar el color
↓
Mostrar resultat
```

---

## Per què s'utilitza HSV?

Les imatges que llegeix OpenCV estan en format **BGR**, però per detectar colors és més còmode utilitzar **HSV**.

HSV separa la informació en:

```txt
H = Hue / To del color
S = Saturation / Intensitat del color
V = Value / Brillantor
```

Això permet diferenciar millor colors com:

- blau,
- verd,
- groc,
- taronja,
- vermell,
- marró.

Per exemple, dos colors poden semblar semblants en RGB, però en HSV es poden separar millor segons el seu to, saturació i brillantor.

---

## Lectura robusta d'imatges

El codi no utilitza directament:

```python
cv2.imread()
```

perquè en Windows pot donar problemes quan la ruta conté accents o caràcters especials, com per exemple:

```txt
Pràctiques
```

Per això es fa servir una lectura més robusta:

```python
datos = np.fromfile(str(ruta_imagen), dtype=np.uint8)
imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)
```

Això evita errors de lectura de fitxers en rutes amb accents.

---

## Cerca automàtica d'imatges

El programa busca automàticament imatges dins la carpeta actual.

Accepta extensions:

```txt
.jpg
.jpeg
.JPG
.JPEG
.png
.PNG
```

A més, evita duplicats, ja que en Windows les extensions `.jpg` i `.JPG` poden arribar a detectar el mateix fitxer dues vegades.

---

## Detecció del Skittle

Primer es crea una màscara per detectar zones amb color viu:

```python
lower = np.array([0, 70, 45])
upper = np.array([179, 255, 255])
mascara = cv2.inRange(hsv, lower, upper)
```

Aquesta màscara intenta quedar-se amb les parts de la imatge que tenen color suficient i descartar parts com:

- fons de fusta,
- ombres,
- zones grises,
- reflexos poc saturats.

Després es busquen contorns amb:

```python
cv2.findContours()
```

---

## Selecció del contorn correcte

Inicialment, el programa agafava el contorn més gran, però això podia fallar perquè altres zones de la imatge, com objectes a la part inferior, també tenien colors vius.

Per solucionar-ho, ara el programa selecciona el contorn que més sembla un Skittle segons diversos criteris:

```txt
- Ha de tenir una àrea raonable.
- Ha de ser relativament circular.
- No pot tocar les vores de la imatge.
- No pot ser una regió massa gran.
- No pot ser massa allargat.
- Es prioritzen objectes propers al centre de la imatge.
```

Això permet evitar detectar erròniament altres objectes de la imatge.

---

## Càlcul del color dominant

Un cop detectat el contorn del Skittle, es crea una màscara només per aquest objecte.

Després es calculen els valors HSV dels píxels que pertanyen al Skittle.

Per evitar que els reflexos blancs o les ombres afectin massa, es filtra la saturació i es fa servir la **mediana** en comptes de la mitjana:

```python
h_median = float(np.median(pixels_h))
s_median = float(np.median(pixels_s))
v_median = float(np.median(pixels_v))
```

La mediana és més robusta que la mitjana perquè no es veu tan afectada per valors extrems, com reflexos molt blancs o zones molt fosques.

---

## Classificació del color

La funció principal de classificació és:

```python
clasificar_color_hsv(h, s, v)
```

Aquesta funció rep els valors HSV dominants i retorna un color.

Els rangs utilitzats són aproximadament:

```txt
H < 10 o H >= 170     -> vermell
10 <= H < 24          -> taronja
24 <= H < 40          -> groc
40 <= H < 85          -> verd
85 <= H < 130         -> blau
130 <= H < 160        -> lila / morat
```

També s'ha afegit una regla especial per detectar el color marró.

---

## Diferència entre vermell i marró

En HSV, el marró pot caure en una zona semblant al vermell o taronja. Per això no n'hi ha prou amb mirar només el valor `H`.

En les imatges de prova:

```txt
marró   -> H proper al vermell/taronja, però amb V baix i S més baixa
vermell -> H proper al vermell, però amb V alta i S alta
```

Per això el codi detecta el marró així:

```python
if (h < 20 or h >= 170) and v < 130 and s < 180:
    return "marro"
```

És a dir:

```txt
Si sembla vermell/taronja,
però és fosc i menys saturat,
llavors es classifica com a marró.
```

---

## Visualització del resultat

Per cada imatge, el programa mostra una finestra amb:

- la imatge original,
- un rectangle verd al voltant del Skittle,
- un punt al centre aproximat,
- el nom del fitxer,
- el color detectat.

Exemple visual:

```txt
prova1.jpg: blau
```

Per passar a la següent imatge, cal prémer qualsevol tecla mentre la finestra d'OpenCV està seleccionada.

---

## Resultat esperat

Un exemple de sortida per terminal és:

```txt
Resultats:
------------------------------------------------------------
prova1.jpg -> blau (H=115.0, S=255.0, V=211.0)
prova2.jpg -> groc (H=28.0, S=249.0, V=221.0)
prova3.jpg -> marro (H=9.0, S=115.0, V=70.0)
prova4.jpg -> taronja (H=14.0, S=243.0, V=223.0)
prova5.jpg -> verd (H=77.0, S=238.0, V=191.0)
prova6.jpg -> vermell (H=176.0, S=224.0, V=201.0)

RESUM FINAL
------------------------------------------------------------
prova1.jpg -> blau
prova2.jpg -> groc
prova3.jpg -> marro
prova4.jpg -> taronja
prova5.jpg -> verd
prova6.jpg -> vermell
```

---

## Colors detectats

Actualment el codi pot classificar:

```txt
blau
groc
marro
taronja
verd
vermell
lila / morat
rosa / vermell clar
blanc / gris clar
molt fosc / ombra
```

Els colors principals de la prova són:

```txt
blau
groc
marro
taronja
verd
vermell
```

---

## Limitacions

Aquest sistema és una primera versió basada en regles HSV.

Pot fallar si:

- canvia molt la il·luminació,
- hi ha ombres fortes,
- el fons té colors semblants al Skittle,
- el Skittle està molt lluny o molt petit,
- hi ha més d'un objecte circular de color a la imatge,
- la càmera canvia molt la saturació o la brillantor.

Per un sistema final, seria recomanable:

- controlar millor la il·luminació,
- fixar la posició de la càmera,
- posar un fons més neutre,
- calibrar els rangs HSV amb més imatges,
- guardar exemples de cada color,
- provar amb vídeo en temps real.

---

## Possible evolució amb Raspberry Pi

Aquest codi és una prova local amb imatges ja capturades.

Més endavant, en una Raspberry Pi, el flux seria:

```txt
Capturar imatge amb la càmera
↓
Executar detecció de color
↓
Classificar el Skittle
↓
Enviar ordre al robot o mecanisme de separació
```

Per exemple:

```txt
Si color = vermell -> moure servo a posició 1
Si color = blau    -> moure servo a posició 2
Si color = verd    -> moure servo a posició 3
```

---

## Resum

Aquest codi implementa una primera versió funcional d'un detector de color per Skittles utilitzant visió per computador.

La detecció es basa en:

- OpenCV,
- conversió a HSV,
- màscares de color,
- detecció de contorns,
- selecció de formes circulars,
- classificació del color dominant.

És una base inicial per al sistema de separació automàtica de Skittles del projecte.
