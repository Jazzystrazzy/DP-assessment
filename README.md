Korte README

Deze repo bevat twee projecten. Het project waar ik oorspronkelijk mee aan de slag was (waarbij uiteindelijk bleek dat ik op onverklaarbare wijze de opdracht verkeerd had begrepen), en een map genaamd "example_dag_airflow". Het een heeft dus niets met het ander te maken. Ik heb deze map nog toegevoegd zodat ik toch kon laten zien op welk niveau ik op dit moment ben. Het betreft een pipeline die ik de afgelopen dagen heb gebouwd voor een klant, en bevat zijn eigen README.md met uitleg.

De rest van deze repo staat in het teken van het oorspronkelijke project. Ik heb hierbij gekozen voor het maken van een Django webapp die in een server van Azure draait, wat voor mij een nieuwe ervaring was, maar een mooi idee leek voor deze assessment. Let wel dat dit project verre van af is. Ik heb er ongeveer 6 uur aan gewerkt en me toen gerealiseerd dat dit niet helemaal de bedoeling was. Hopelijk kan ik morgen toch nog toelichten welke stappen nog nodig waren en waar ik tegenaan liep. Het plan was om een applicatie te maken waarop je snel het weer (de sneeuw) op je favoriete skibestemming kunt zien. Aan de achterkant zou de database bij kunnen houden welke skibestemmingen het populairst zijn, daar continu weerdata voor kunnen verzamelen en zo kijken welke locatie bijvoorbeeld de beste sneewbeschikbaarheid geeft in welke tijden van het jaar.

De app functioneert wel deels, en is te bekijken via onderstaande link:
https://skiapp-g6agcrebcqg4bzbf.northeurope-01.azurewebsites.net/

Er gebeurt helaas nog niets met de data die door de app wordt opgevraagd. De data wordt rechtstreeks opgehaald van de API, maar wordt nog niet getransformeerd of weggeschreven naar een database.