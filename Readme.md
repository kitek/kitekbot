Kitekbot
====================

Kitekbot jest botem XMPP stworzonym w Pythonie i opartym o Google App Engine.
* * *
Obecnie bot obs�uguje nast�puj�ce funkcje / komendy:

- **/help** - wy�wietla dost�pne komendy wraz z kr�tkim opisem
- **/info** *wiadomo��* - wysy�a wiadomo�� do wszystkich u�ytkownik�w
- **/sync** *plik1 plik2* - wysy�a wiadomo�� o synchronizowanych plikach i oczekuje na odpowied�
- **/sync** *on|off* - w�/wy� otrzymywanie informacji o synchronizowanych plikach
- **/online** - wy�wietla wszystkich u�ytkownik�w wraz ich statusami
- **/join** *nazwaPokoju* - tworzy i subskrybuje podany pok�j
- **/leave** *nazwaPokoju* - opuszcza wybrany pok�j
- **/rooms** - wy�wietla list� wszystkich dost�pnych pokoi
- **/rooms** *nazwaPokoju* - wy�wietla informacje o wybranym pokoju
- **/invite** *user nazwaPokoju* - zaprasza u�ytkownika do wybranego pokoju
- **/switch** *nazwaPokoju* - umo�liwia prze��czanie si� pomi�dzy pokojami

### Przesy�anie wiadomo�ci ######
Pisanie wiadomo�ci do wszystkich u�ytkownik�w mo�liwe jest na dwa sposoby: 

- napisanie wiadomo�ci bez �adnej komendy
- u�ycie komendy /info

Pisanie wiadomo�ci w konkretnym pokoju mo�liwe jest poprzez:

- podawanie na pocz�tku wiadomo�ci *#nazwaPokoju* np.: *#tech Jest tam kto�?* wy�le wiadomo�� do pokoju o nazwie *tech* (oczywi�cie wymagana jest wcze�niejsza subskrypcja)
- wcze�niejsze prze��czenie si� do pokoju i wys�anie wiadomo�ci bez �adnych parametr�w np: 

> */switch tech*
>
> Jest tam kto�?

