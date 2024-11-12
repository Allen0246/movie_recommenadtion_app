# Filmajánló applikáció

## Applikáció elindítása és bekonfigurálása szükséges lépések
* Docker letöltése az alábbi linkről: ```https://www.docker.com/products/docker-desktop/```
* Bármilyen terminálon el lehet indítani, az alábbi paranccsal : ```docker-compose up -d --build```
* Ha a web konténer ezt a hiba üzenetet írja ki ```exec ./start.sh: no such file or directory```, akkor módosítani kell a ```start.sh``` fájl End Of Line Sequence-ét ```CRLF-ről LF-re```
* Ha nem csak az aktuális dátum szerinti filmeket,sorozatokat szeretnénk látni akkor megkell változtatni a letöltéshez megadott dátumot.
    - A ```.env``` fájlban ```PRIMARY_RELEASE_DATE_GTE-nek``` megkell adni azt a dátumot amelytől jelenlegi dátumig letöltse a filmeket,sorozatokat.
    - A ```services/web/project/extensions/REST_THEMOVIEDB.py``` fájlban a 109. sor elé egy ```#``` jelet kell rakni majd a 108. sornál törölni a ```#``` jelet, így nem csak a mai időintervallumban keres filmeket, hanem a fentebb megatobb ```PRIMARY_RELEASE_DATE_GTE``` szerint.

## Applikáció alap beállításai
* Az applikáció indítása során létrejön egy ```default admin``` felhasználó, aminek a felhaszáló neve és jelszava ```admin``` lesz.
* Az applikáció indítása során létrejön egy ```default user``` felhasználó, aminek a felhaszáló neve és jelszava ```user``` lesz.
* Az applikáció a 1334-es porton érhető el ```https://localhost:1334```.
* A postgresql default portja az ```5432```.
* Az adatbázis default beállításait a ```.env ``` fájlban lehet megtalálni a ```# Database settings``` alatt.

## Applikáció felépítése során használt technológiák, keretrendszerek.
* Python
* Flask
* Postgresql
* Nginx
* Bootstrap
* datatables

## Applikáció további beállítása
Látogass el a ```https://www.themoviedb.org/``` oldalra és hozz létre egy fiókot, igényelj egy API kulcsot, majd az ```.env``` fájlba ird be a ***THEMOVIEDB_TOKEN-hez***. <br>
Állítsd be a ```SECRET_KEY-hez``` és a ```WTF_CSRF_SECRET_KEY-hez``` random betükből és számokból álló karaktersort, ez lehet tetszőleges hosszúságú. 

## Applikáció használata
* Ha nem default ```usert``` vagy default ```admint``` szeretnénk használni, hozzunk létre egy fiókot a ```https://localhost:1334/register``` oldalon.
* Jelentkezzünk be az általunk választott felhasználói adatokkal.
* Nem ```admin``` felhasználóként az alábbiakat tudjuk elérni:
    - Home page 
        - *ez az oldal az applikáció főoldala.*
    - Movies 
        - *itt jelennek meg az adatbázisba letöltött filmek az előzőekben megadott, számunkra megfelelő időintervallumban. ```Update``` gombbal tudjuk frissíteni a listát, ```Export``` gombbal pedig le tudjuk tölteni őket egy excel fájlba.*
    - My movies 
        - *ebben a menüpontban találhatóak azok a filmek, amelyeket már korábban bejelöltünk megtekintetként, hozzá adtunk egy megtekintési dátumot, valamint értékelést. Lehetőség van a filmet eltávolítani ebből a listából, illetve újra megnézettnek jelölni, amivel frissíteni lehet az értékelésünket, illetve a korábban megadott dátumot. ```Export``` gombbal ezeknek a listáját is letudjuk tölteni egy excel fájlba.*
    - Movie recommendation 
        - *itt tudunk film/sorozat ajánlást kérni műfajok szerint, az adatbázisban már meglévő filmek közül.*
    - Log out 
        - *kijelentkezési lehetőség.*
* ```admin``` felhasználóként elérhető plusz menüpontok:
    - User 
        - *itt láthatjuk a már meglévő felhasználókat, ezeket tudjuk  modosítani valamint törölni. Továbbá itt tudunk új felhasználókat is létrehozni.*
    - System log 
        - *itt tudjuk megtekinteni, illetve letölteni a logokat, amiket az applikáció létrehoz.*
