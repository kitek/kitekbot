Kitekbot
====================

Kitekbot jest botem XMPP stworzonym w Pythonie i opartym o Google App Engine.
* * *
Obecnie bot obs³uguje nastêpuj¹ce funkcje / komendy:

- **/help** - wyœwietla dostêpne komendy wraz z krótkim opisem
- **/info** *wiadomoœæ* - wysy³a wiadomoœæ do wszystkich u¿ytkowników
- **/sync** *plik1 plik2* - wysy³a wiadomoœæ o synchronizowanych plikach i oczekuje na odpowiedŸ
- **/sync** *on|off* - w³/wy³ otrzymywanie informacji o synchronizowanych plikach
- **/online** - wyœwietla wszystkich u¿ytkowników wraz ich statusami
- **/join** *nazwaPokoju* - tworzy i subskrybuje podany pokój
- **/leave** *nazwaPokoju* - opuszcza wybrany pokój
- **/rooms** - wyœwietla listê wszystkich dostêpnych pokoi
- **/rooms** *nazwaPokoju* - wyœwietla informacje o wybranym pokoju
- **/invite** *user nazwaPokoju* - zaprasza u¿ytkownika do wybranego pokoju
- **/switch** *nazwaPokoju* - umo¿liwia prze³¹czanie siê pomiêdzy pokojami

### Przesy³anie wiadomoœci ######
Pisanie wiadomoœci do wszystkich u¿ytkowników mo¿liwe jest na dwa sposoby: 

- napisanie wiadomoœci bez ¿adnej komendy
- u¿ycie komendy /info

Pisanie wiadomoœci w konkretnym pokoju mo¿liwe jest poprzez:

- podawanie na pocz¹tku wiadomoœci *#nazwaPokoju* np.: *#tech Jest tam ktoœ?* wyœle wiadomoœæ do pokoju o nazwie *tech* (oczywiœcie wymagana jest wczeœniejsza subskrypcja)
- wczeœniejsze prze³¹czenie siê do pokoju i wys³anie wiadomoœci bez ¿adnych parametrów np: 

> */switch tech*
>
> Jest tam ktoœ?

