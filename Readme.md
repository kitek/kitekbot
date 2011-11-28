Kitekbot
====================

Kitekbot jest botem XMPP stworzonym w Pythonie i opartym o Google App Engine.
* * *
Obecnie bot obsługuje następujące funkcje / komendy:

- **/help** - wyświetla dostępne komendy wraz z krótkim opisem
- **/info** *wiadomość* - wysyła wiadomość do wszystkich użytkowników
- **/sync** *plik1 plik2* - wysyła wiadomość o synchronizowanych plikach i oczekuje na odpowiedź
- **/sync** *on|off* - wł/wył otrzymywanie informacji o synchronizowanych plikach
- **/online** - wyświetla wszystkich użytkowników wraz ich statusami
- **/join** *nazwaPokoju* - tworzy i subskrybuje podany pokój
- **/leave** *nazwaPokoju* - opuszcza wybrany pokój
- **/rooms** - wyświetla listę wszystkich dostępnych pokoi
- **/rooms** *nazwaPokoju* - wyświetla informacje o wybranym pokoju
- **/invite** *user nazwaPokoju* - zaprasza użytkownika do wybranego pokoju
- **/switch** *nazwaPokoju* - umożliwia przełączanie się pomiędzy pokojami

### Przesyłanie wiadomości ######
Pisanie wiadomości do wszystkich użytkowników możliwe jest na dwa sposoby: 

- napisanie wiadomości bez żadnej komendy
- użycie komendy /info

Pisanie wiadomości w konkretnym pokoju możliwe jest poprzez:

- podawanie na początku wiadomości *#nazwaPokoju* np.: *#tech Jest tam ktoś?* wyśle wiadomość do pokoju o nazwie *tech* (oczywiście wymagana jest wcześniejsza subskrypcja)
- wcześniejsze przełączenie się do pokoju i wysłanie wiadomości bez żadnych parametrów np: 

> */switch tech*
>
> Jest tam ktoś?

