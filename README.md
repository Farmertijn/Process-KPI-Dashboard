# Process KPI Dashboard

## 📊 Overzicht
De **Process KPI Dashboard** is een interactieve applicatie gebouwd met **Dash** en **Flask**, ontworpen om Key Performance Indicators (KPI's) te visualiseren en analyseren. Deze tool biedt gebruikers inzichten in gegevensstromen, zoals in- en uitvoer, prestaties, en efficiëntie binnen productieprocessen. Het dashboard is specifiek afgestemd op datagestuurde omgevingen waarbij responsiviteit en gebruiksvriendelijkheid cruciaal zijn.

---

## 🔧 Functionaliteiten
- **Interactieve KPI-weergave**: Visualiseer gegevens zoals totale opbrengst, infeed, outfeed, en meer.
- **Grafieken en tabellen**: Dynamische grafieken die eenvoudig kunnen worden gefilterd op tijdsperiodes (Today, Yesterday, Last Week).
- **Gebruikersbeheer**: Inclusief inlogfunctionaliteit en onderscheid tussen admin- en standaardgebruikers.

---

## 📂 Projectstructuur
Een korte uitleg van de belangrijkste mappen en bestanden:
```
📆Process-KPI-Dashboard
├── app.py               # Dash-app configuratie
├── calculate.py         # Berekeningen en filtering van KPI-data
├── charts.py            # Genereren van grafieken met matplotlib
├── data.py              # Inlezen van data uit SQL-database of CSV-backup
├── harvester.py         # KPI's gerelateerd aan oogstdata
├── InOut.py             # KPI's voor in- en uitvoer
├── home.py              # Home-dashboard en navigatie
├── index.py             # Hoofdbestand voor het starten van de applicatie
├── models.py            # Gebruikersmodel voor authenticatie
├── requirements.txt     # Lijst van vereiste Python-pakketten
└── README.md            # Documentatie
```

---

## 🚀 Installatie en Gebruik
Volg deze stappen om de applicatie lokaal te draaien:

1. **Clone de repository:**
   ```bash
   git clone https://github.com/Farmertijn/Process-KPI-Dashboard.git
   cd Process-KPI-Dashboard
   ```

2. **Installeer de vereisten:**
   Zorg ervoor dat je Python 3.8+ geïnstalleerd hebt.

3. **Start de applicatie:**
   ```bash
   python index.py
   ```
   De applicatie installeert zelf de benodigde packages en draait daarna lokaal op [http://127.0.0.1:5000/](http://127.0.0.1:5000/).
   

5. **Log in:**
   - **Admin gebruikersnaam:** `admin`
   - **Wachtwoord:** `admin123`
  
   - **Test gebruikersnaam** `test`
   - **Wachtwoord** `test123`
