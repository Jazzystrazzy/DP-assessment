Dit is een voorbeeld van een Apache Airflow pipeline die ik vandaag heb afgerond voor een klant.
In de airflow_home folder vind je een aantal mappen:
    - /plugins waar in dit geval de map /notifiers in zit met een /slack notifier, zodat we een melding in een slack kanaal krijgen als een taak faalt.
    - /dags waar de map /genesys in zit, een software pakket dat communicatiemiddelen in een organisatie logt. in /dags/genesys vind je:
        - dag.py waar de hoofdstructuur van de DAGs worden gespecificeerd. 
        - /tasks, waar de airflow taken worden gedefinieerd in tasks.py en de helper taken worden gedefinieerd in helpers.py.
        - /configs, waar de configuratie jsons in staan die worden gebruikt om namen van connecties op te slaan en eenvoudig DAGS, endpoints, tabellen en kolommen toe te voegen aan de ontsluiting.  
        - /templates, met de copy en upsert query die gebruikt worden om data respectievelijk van azure naar het staging schema te laden, en data van staging naar productie schema te upserten.

Verder vind je wat instellingen voor linters en dergelijke, maar nog belangrijker, het mapje /sql. In dit mapje staan de SQL queries die gebruikt worden om de tabellen aan te maken waar de uiteindelijke data in terecht komt.
In ons geval is dat altijd een PostgresQL database.

Excuses voor de beknopte readME, maar ik ben net een half uur thuis en het is inmiddels 19:09 uur. Hopelijk kun je er toch al wat van meekrijgen.