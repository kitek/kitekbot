Kitekbot
====================

Kitekbot jest botem XMPP stworzonym w Pythonie i opartym o [Google App Engine](https://developers.google.com/appengine/ "GAE").

Jego główną funkcjonalnością jest możliwość prowadzenia rozmów grupowych na kanale głównym lub we własnych pokojach.

Dodatkowo Bot obsługuje zestaw kilku komend, które mogą zostać rozszerzone lub dostosowane do własnych potrzeb:

* * *
Lista komend:

- **/help [nazwaKomendy]** - Informacje o dostępnych komendach bot'a (aliasy: pomoc).
- **/rooms [nazwaPokoju]** - Lista dostępnych pokoi utworzonych przez użytkowników (alias: pokoje).
- **/join nazwaPokoju** - Subskrybuje podany pokój. Jeżeli taki nie istnieje również go tworzy (alias: dolacz).
- **/leave nazwaPokoju** - Usuwa subskrypcję z danego pokoju (alias: opusc).
- **/switch nazwaPokoju** - Zmienia pokój w którym domyślnie piszemy.
- **/invite emailUzytkownika nazwaPokoju** - Zaprasza danego użytkownika do wybranego pokoju (alias: zapros).
- **/set [nazwa] [wartosc]** - Wyświetla lub zmienia ustawienia użytkownika (alias: ustaw).
- **/last [nazwaPokoju] [limit]** - Lista ostatnich rozmów.
- **/surl Url** - Skraca podany link (alias: tnij).
- **/version** - Aktualna kompilacja Bot'a (alias: wersja).
- **/online** - Lista użytkowników online.
- **/offline** - Lista użytkowników offline.
- **/quota** - Informacje o statusie wykorzystywanych przez Bot'a usług.
- **/setstatus status** - Ustawia XMPP status dla bot'a.
- **/inviteuser emailUzytkownika** - Zaprasza nowego użytkownika do systemu (roster'a Bot'a).

### Wysyłanie wiadomości ###

Pisanie wiadomości na kanale głównym ('global' - każdy domyślnie ten kanał subskrybuje) odbywa się przez wpisanie treści i wciśnięcie
klawisza ENTER.

Pisanie do konkretnego pokoju możliwe jest przez podanie na początku naszej wiadomości _#nazwaPokoju_. 

Na przykład wysłanie wiadomości do pokoju "pomoc" wygląda tak: _#pomoc Hey, czy ktoś potrzebuje pomocy?_

### Pokoje ###

Każdy z użytkowników ma możliwość tworzenia własnych, dołączania, zapraszania i opuszczania pokoju.

Pokoje pełnią rolę osobnych czatów np. tematycznych i istnieją w celu nie zaśmiecania kanału głównego.

Istnieje możliwość przełączenia domyślnego pisania wiadomości na konkretny pokój (nie trzeba wtedy przed treścią wiadomości podawać #nazwaPokoju).

Powyższą funkcjonalność realizuje komenda "switch" (np _/switch pomoc_). Oczywiście istnieje zawsze możliwość powrotu do pokoju głównego przez podanie _/switch global_.

Będąc przełączony na konretny pokój istnieje możliwość wysłania wiadomości na czat główny za pomocą konstrukcji: __## treść wiadomości__.

### Ustawienia ###

Każdy użytkownik ma możliwość pewnej konfiguracji Bot'a.

Lista dostępnych ustawień i ich wartości:

- **offlineChat [enabled|disabled]** - Otrzymywanie wiadomości gdy jesteśmy offline.
- **globalChat [enabled|disabled]** - Otrzymywanie wiadomości z czatu globalnego.
