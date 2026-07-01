import streamlit as st
import urllib.request
import json as _json
import streamlit.components.v1 as components
import urllib.request
import json as _json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os, itertools
from datetime import datetime, timezone

def confetti():
    js = """<div id="cf" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;"></div>
<script>
(function(){var c=['#4ade80','#fbbf24','#22d3ee','#f472b6','#a78bfa'];var n=document.getElementById('cf');
for(var i=0;i<80;i++){var e=document.createElement('div');
e.style.cssText='position:absolute;width:'+(Math.random()*10+5)+'px;height:'+(Math.random()*10+5)+'px;background:'+c[Math.floor(Math.random()*c.length)]+';border-radius:'+(Math.random()>.5?'50%':'2px')+';left:'+Math.random()*100+'%;top:-20px;';
n.appendChild(e);e.animate([{transform:'translateY(0) rotate(0deg)',opacity:1},{transform:'translateY(100vh) rotate(720deg)',opacity:0}],{duration:(Math.random()*2+1.5)*1000,delay:Math.random()*800,fill:'forwards'});}
setTimeout(function(){n.remove();},4000);})();
</script>"""
    st.markdown(js, unsafe_allow_html=True)

WC_START = datetime(2026,6,11,20,0,0,tzinfo=timezone.utc)

API_NAME_MAP = {
    "Czech Republic": "Czechia",
    "Bosnia & Herzegovina": "Bosnia-Herzegovina",
    "USA": "United States",
    "DR Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Turkey": "Türkiye",
    "Turkiye": "Türkiye",
    "Curacao": "Curaçao",
    "Côte d'Ivoire": "Ivory Coast",
    "Cabo Verde": "Cape Verde",
}

@st.cache_data(ttl=300)
def fetch_live_scores():
    try:
        url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=6)
        data = _json.loads(resp.read())
        scores = {}
        for m in data.get("matches", []):
            t1 = m.get("team1","").strip()
            t2 = m.get("team2","").strip()
            score = m.get("score", {})
            ft = score.get("ft")
            ht = score.get("ht")
            goals1 = m.get("goals1", [])
            goals2 = m.get("goals2", [])
            t1 = API_NAME_MAP.get(t1, t1)
            t2 = API_NAME_MAP.get(t2, t2)
            key = f"{t1}|{t2}"
            scores[key] = {
                "ft": ft,         # [g1, g2] or None if not played
                "et": score.get("et"),
                "p": score.get("p"),
                "ht": ht,
                "goals1": goals1,
                "goals2": goals2,
                "date": m.get("date",""),
            }
        return scores
    except:
        return {}

def get_match_score(team1, team2, live_scores):
    # Try both directions
    for k in [f"{team1}|{team2}", f"{team2}|{team1}"]:
        if k in live_scores:
            s = live_scores[k]
            ft = s.get("ft")
            if ft:
                if k == f"{team1}|{team2}":
                    return ft[0], ft[1], s.get("goals1",[]), s.get("goals2",[])
                else:
                    return ft[1], ft[0], s.get("goals2",[]), s.get("goals1",[])
    return None, None, [], []

st.set_page_config(
    page_title="Kickoff 26 — Your Guide to the 2026 World Cup",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── FLAGS ─────────────────────────────────────────────────────────────────
FLAGS = {
    "ENG":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","FRA":"🇫🇷","ESP":"🇪🇸","GER":"🇩🇪","ITA":"🇮🇹",
    "ARG":"🇦🇷","BRA":"🇧🇷","NED":"🇳🇱","POR":"🇵🇹","BEL":"🇧🇪",
    "MAR":"🇲🇦","COD":"🇨🇩","URU":"🇺🇾","SEN":"🇸🇳","AUT":"🇦🇹",
    "NOR":"🇳🇴","CRO":"🇭🇷","COL":"🇨🇴","USA":"🇺🇸","CIV":"🇨🇮",
    "PAR":"🇵🇾","BIH":"🇧🇦","GHA":"🇬🇭","ALG":"🇩🇿","SUI":"🇨🇭",
    "CZE":"🇨🇿","AUS":"🇦🇺","ECU":"🇪🇨","CAN":"🇨🇦","KOR":"🇰🇷",
    "MEX":"🇲🇽","JPN":"🇯🇵","SWE":"🇸🇪","TUN":"🇹🇳","SCO":"🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "CPV":"🇨🇻","KSA":"🇸🇦","RSA":"🇿🇦","IRQ":"🇮🇶","JOR":"🇯🇴",
    "UZB":"🇺🇿","QAT":"🇶🇦","IRN":"🇮🇷","NZL":"🇳🇿","PAN":"🇵🇦",
    "HAI":"🇭🇹","CUW":"🇨🇼","TUR":"🇹🇷","EGY":"🇪🇬","SVN":"🇸🇮",
}

# Primary flag-accent color per nation code, used as a subtle left-border
# accent on bracket team rows so each team carries its national color identity.
TEAM_COLORS = {
    "RSA":"#007A4D","CAN":"#FF0000","BRA":"#009739","JPN":"#BC002D",
    "GER":"#DD0000","PAR":"#D52B1E","NED":"#FF6F00","MAR":"#C1272D",
    "CIV":"#FF8200","NOR":"#BA0C2F","FRA":"#0055A4","SWE":"#006AA7",
    "MEX":"#006847","ECU":"#FFD100","ENG":"#CE1124","COD":"#007FFF",
    "BEL":"#ED2939","SEN":"#00853F","USA":"#3C3B6E","BIH":"#002395",
    "ESP":"#AA151B","AUT":"#ED2939","SUI":"#FF0000","ALG":"#006233",
    "POR":"#006600","CRO":"#FF0000","AUS":"#00008B","EGY":"#CE1126",
    "ARG":"#74ACDF","CPV":"#003893","COL":"#FCD116","GHA":"#006B3F",
}

NATION_TO_CODE = {
    "Mexico":"MEX","South Africa":"RSA","South Korea":"KOR","Czechia":"CZE",
    "Canada":"CAN","Bosnia-Herzegovina":"BIH","Qatar":"QAT","Switzerland":"SUI",
    "Brazil":"BRA","Morocco":"MAR","Haiti":"HAI","Scotland":"SCO",
    "United States":"USA","Paraguay":"PAR","Australia":"AUS","Türkiye":"TUR",
    "Germany":"GER","Curaçao":"CUW","Ivory Coast":"CIV","Ecuador":"ECU",
    "Netherlands":"NED","Japan":"JPN","Sweden":"SWE","Tunisia":"TUN",
    "Belgium":"BEL","Egypt":"EGY","Iran":"IRN","New Zealand":"NZL",
    "Spain":"ESP","Cape Verde":"CPV","Saudi Arabia":"KSA","Uruguay":"URU",
    "France":"FRA","Senegal":"SEN","Iraq":"IRQ","Norway":"NOR",
    "Argentina":"ARG","Algeria":"ALG","Austria":"AUT","Jordan":"JOR",
    "Portugal":"POR","DR Congo":"COD","Uzbekistan":"UZB","Colombia":"COL",
    "England":"ENG","Croatia":"CRO","Ghana":"GHA","Panama":"PAN",
}

# FIFA Rankings (April 2026)
FIFA_RANKINGS = {
    "ARG":1,"FRA":3,"ESP":2,"ENG":4,"POR":5,"BRA":6,"MAR":7,"NED":8,
    "BEL":9,"GER":10,"CRO":11,"COL":13,"MEX":14,"SEN":15,"URU":16,
    "USA":17,"JPN":18,"SUI":19,"TUR":22,"AUT":24,"KOR":25,"AUS":27,
    "ALG":28,"EGY":29,"CAN":30,"NOR":31,"SCO":42,"TUN":46,"COD":45,
    "UZB":50,"QAT":57,"KSA":61,"RSA":60,"BIH":64,"CPV":67,"GHA":73,
    "PAN":34,"HAI":83,"CUW":82,"NZL":85,"IRQ":56,"IRN":21,"JOR":63,
    "PAR":40,"CZE":39,"CIV":33,"ECU":23,"SWE":38,"KSA":61,
}

GROUPS = {
    "A":["Mexico","South Africa","South Korea","Czechia"],
    "B":["Canada","Bosnia-Herzegovina","Qatar","Switzerland"],
    "C":["Brazil","Morocco","Haiti","Scotland"],
    "D":["United States","Paraguay","Australia","Türkiye"],
    "E":["Germany","Curaçao","Ivory Coast","Ecuador"],
    "F":["Netherlands","Japan","Sweden","Tunisia"],
    "G":["Belgium","Egypt","Iran","New Zealand"],
    "H":["Spain","Cape Verde","Saudi Arabia","Uruguay"],
    "I":["France","Senegal","Iraq","Norway"],
    "J":["Argentina","Algeria","Austria","Jordan"],
    "K":["Portugal","DR Congo","Uzbekistan","Colombia"],
    "L":["England","Croatia","Ghana","Panama"],
}

WC_SCHEDULE = [
    # ── GROUP A ───────────────────────────────────────────────────────────
    {"group":"A","team1":"Mexico","team2":"South Africa","date":"Jun 11","time":"3:00 PM ET","venue":"Estadio Azteca","city":"Mexico City"},
    {"group":"A","team1":"South Korea","team2":"Czechia","date":"Jun 11","time":"10:00 PM ET","venue":"Estadio Akron","city":"Guadalajara"},
    {"group":"A","team1":"Mexico","team2":"South Korea","date":"Jun 18","time":"9:00 PM ET","venue":"Estadio Akron","city":"Guadalajara"},
    {"group":"A","team1":"Czechia","team2":"South Africa","date":"Jun 18","time":"12:00 PM ET","venue":"Mercedes-Benz Stadium","city":"Atlanta"},
    {"group":"A","team1":"Czechia","team2":"Mexico","date":"Jun 24","time":"9:00 PM ET","venue":"Estadio Azteca","city":"Mexico City"},
    {"group":"A","team1":"South Africa","team2":"South Korea","date":"Jun 24","time":"9:00 PM ET","venue":"Estadio BBVA","city":"Monterrey"},
    # ── GROUP B ───────────────────────────────────────────────────────────
    {"group":"B","team1":"Canada","team2":"Bosnia-Herzegovina","date":"Jun 12","time":"3:00 PM ET","venue":"BMO Field","city":"Toronto"},
    {"group":"B","team1":"Qatar","team2":"Switzerland","date":"Jun 13","time":"3:00 PM ET","venue":"Levi's Stadium","city":"Santa Clara"},
    {"group":"B","team1":"Canada","team2":"Qatar","date":"Jun 18","time":"6:00 PM ET","venue":"BC Place","city":"Vancouver"},
    {"group":"B","team1":"Switzerland","team2":"Bosnia-Herzegovina","date":"Jun 18","time":"9:00 PM ET","venue":"SoFi Stadium","city":"Los Angeles"},
    {"group":"B","team1":"Switzerland","team2":"Canada","date":"Jun 24","time":"3:00 PM ET","venue":"BC Place","city":"Vancouver"},
    {"group":"B","team1":"Bosnia-Herzegovina","team2":"Qatar","date":"Jun 24","time":"3:00 PM ET","venue":"Lumen Field","city":"Seattle"},
    # ── GROUP C ───────────────────────────────────────────────────────────
    {"group":"C","team1":"Brazil","team2":"Morocco","date":"Jun 13","time":"6:00 PM ET","venue":"MetLife Stadium","city":"New York/NJ"},
    {"group":"C","team1":"Haiti","team2":"Scotland","date":"Jun 13","time":"9:00 PM ET","venue":"Gillette Stadium","city":"Boston"},
    {"group":"C","team1":"Brazil","team2":"Haiti","date":"Jun 19","time":"8:30 PM ET","venue":"Lincoln Financial Field","city":"Philadelphia"},
    {"group":"C","team1":"Scotland","team2":"Morocco","date":"Jun 19","time":"6:00 PM ET","venue":"Gillette Stadium","city":"Boston"},
    {"group":"C","team1":"Scotland","team2":"Brazil","date":"Jun 24","time":"6:00 PM ET","venue":"Hard Rock Stadium","city":"Miami"},
    {"group":"C","team1":"Morocco","team2":"Haiti","date":"Jun 24","time":"6:00 PM ET","venue":"Mercedes-Benz Stadium","city":"Atlanta"},
    # ── GROUP D ───────────────────────────────────────────────────────────
    {"group":"D","team1":"United States","team2":"Paraguay","date":"Jun 12","time":"9:00 PM ET","venue":"SoFi Stadium","city":"Los Angeles"},
    {"group":"D","team1":"Australia","team2":"Türkiye","date":"Jun 14","time":"12:00 AM ET","venue":"BC Place","city":"Vancouver"},
    {"group":"D","team1":"United States","team2":"Australia","date":"Jun 19","time":"3:00 PM ET","venue":"Lumen Field","city":"Seattle"},
    {"group":"D","team1":"Türkiye","team2":"Paraguay","date":"Jun 19","time":"11:00 PM ET","venue":"Levi's Stadium","city":"San Francisco"},
    {"group":"D","team1":"Türkiye","team2":"United States","date":"Jun 25","time":"10:00 PM ET","venue":"SoFi Stadium","city":"Los Angeles"},
    {"group":"D","team1":"Paraguay","team2":"Australia","date":"Jun 25","time":"10:00 PM ET","venue":"Levi's Stadium","city":"San Francisco"},
    # ── GROUP E ───────────────────────────────────────────────────────────
    {"group":"E","team1":"Germany","team2":"Curaçao","date":"Jun 14","time":"1:00 PM ET","venue":"NRG Stadium","city":"Houston"},
    {"group":"E","team1":"Ivory Coast","team2":"Ecuador","date":"Jun 14","time":"7:00 PM ET","venue":"Lincoln Financial Field","city":"Philadelphia"},
    {"group":"E","team1":"Germany","team2":"Ivory Coast","date":"Jun 20","time":"4:00 PM ET","venue":"BMO Field","city":"Toronto"},
    {"group":"E","team1":"Ecuador","team2":"Curaçao","date":"Jun 20","time":"8:00 PM ET","venue":"Arrowhead Stadium","city":"Kansas City"},
    {"group":"E","team1":"Curaçao","team2":"Ivory Coast","date":"Jun 25","time":"4:00 PM ET","venue":"Lincoln Financial Field","city":"Philadelphia"},
    {"group":"E","team1":"Ecuador","team2":"Germany","date":"Jun 25","time":"4:00 PM ET","venue":"MetLife Stadium","city":"New York/NJ"},
    # ── GROUP F ───────────────────────────────────────────────────────────
    {"group":"F","team1":"Netherlands","team2":"Japan","date":"Jun 14","time":"4:00 PM ET","venue":"AT&T Stadium","city":"Dallas"},
    {"group":"F","team1":"Sweden","team2":"Tunisia","date":"Jun 14","time":"10:00 PM ET","venue":"Estadio BBVA","city":"Monterrey"},
    {"group":"F","team1":"Netherlands","team2":"Sweden","date":"Jun 20","time":"1:00 PM ET","venue":"NRG Stadium","city":"Houston"},
    {"group":"F","team1":"Tunisia","team2":"Japan","date":"Jun 21","time":"12:00 AM ET","venue":"Estadio BBVA","city":"Monterrey"},
    {"group":"F","team1":"Japan","team2":"Sweden","date":"Jun 25","time":"7:00 PM ET","venue":"AT&T Stadium","city":"Dallas"},
    {"group":"F","team1":"Tunisia","team2":"Netherlands","date":"Jun 25","time":"7:00 PM ET","venue":"Arrowhead Stadium","city":"Kansas City"},
    # ── GROUP G ───────────────────────────────────────────────────────────
    {"group":"G","team1":"Belgium","team2":"Egypt","date":"Jun 15","time":"3:00 PM ET","venue":"Lumen Field","city":"Seattle"},
    {"group":"G","team1":"Iran","team2":"New Zealand","date":"Jun 15","time":"9:00 PM ET","venue":"SoFi Stadium","city":"Los Angeles"},
    {"group":"G","team1":"Belgium","team2":"Iran","date":"Jun 21","time":"3:00 PM ET","venue":"SoFi Stadium","city":"Los Angeles"},
    {"group":"G","team1":"New Zealand","team2":"Egypt","date":"Jun 21","time":"9:00 PM ET","venue":"BC Place","city":"Vancouver"},
    {"group":"G","team1":"New Zealand","team2":"Belgium","date":"Jun 26","time":"11:00 PM ET","venue":"BC Place","city":"Vancouver"},
    {"group":"G","team1":"Egypt","team2":"Iran","date":"Jun 26","time":"11:00 PM ET","venue":"Lumen Field","city":"Seattle"},
    # ── GROUP H ───────────────────────────────────────────────────────────
    {"group":"H","team1":"Spain","team2":"Cape Verde","date":"Jun 15","time":"12:00 PM ET","venue":"Mercedes-Benz Stadium","city":"Atlanta"},
    {"group":"H","team1":"Saudi Arabia","team2":"Uruguay","date":"Jun 15","time":"6:00 PM ET","venue":"Hard Rock Stadium","city":"Miami"},
    {"group":"H","team1":"Spain","team2":"Saudi Arabia","date":"Jun 21","time":"12:00 PM ET","venue":"Mercedes-Benz Stadium","city":"Atlanta"},
    {"group":"H","team1":"Uruguay","team2":"Cape Verde","date":"Jun 21","time":"6:00 PM ET","venue":"Hard Rock Stadium","city":"Miami"},
    {"group":"H","team1":"Cape Verde","team2":"Saudi Arabia","date":"Jun 26","time":"8:00 PM ET","venue":"NRG Stadium","city":"Houston"},
    {"group":"H","team1":"Uruguay","team2":"Spain","date":"Jun 26","time":"8:00 PM ET","venue":"Estadio Akron","city":"Guadalajara"},
    # ── GROUP I ───────────────────────────────────────────────────────────
    {"group":"I","team1":"France","team2":"Senegal","date":"Jun 16","time":"3:00 PM ET","venue":"MetLife Stadium","city":"New York/NJ"},
    {"group":"I","team1":"Iraq","team2":"Norway","date":"Jun 16","time":"6:00 PM ET","venue":"Gillette Stadium","city":"Boston"},
    {"group":"I","team1":"France","team2":"Iraq","date":"Jun 22","time":"5:00 PM ET","venue":"Lincoln Financial Field","city":"Philadelphia"},
    {"group":"I","team1":"Norway","team2":"Senegal","date":"Jun 22","time":"8:00 PM ET","venue":"MetLife Stadium","city":"New York/NJ"},
    {"group":"I","team1":"Norway","team2":"France","date":"Jun 26","time":"3:00 PM ET","venue":"Gillette Stadium","city":"Boston"},
    {"group":"I","team1":"Senegal","team2":"Iraq","date":"Jun 26","time":"3:00 PM ET","venue":"BMO Field","city":"Toronto"},
    # ── GROUP J ───────────────────────────────────────────────────────────
    {"group":"J","team1":"Argentina","team2":"Algeria","date":"Jun 16","time":"9:00 PM ET","venue":"Arrowhead Stadium","city":"Kansas City"},
    {"group":"J","team1":"Austria","team2":"Jordan","date":"Jun 17","time":"12:00 AM ET","venue":"Levi's Stadium","city":"San Francisco"},
    {"group":"J","team1":"Argentina","team2":"Austria","date":"Jun 22","time":"1:00 PM ET","venue":"AT&T Stadium","city":"Dallas"},
    {"group":"J","team1":"Jordan","team2":"Algeria","date":"Jun 22","time":"11:00 PM ET","venue":"Levi's Stadium","city":"San Francisco"},
    {"group":"J","team1":"Jordan","team2":"Argentina","date":"Jun 27","time":"10:00 PM ET","venue":"AT&T Stadium","city":"Dallas"},
    {"group":"J","team1":"Algeria","team2":"Austria","date":"Jun 27","time":"10:00 PM ET","venue":"Arrowhead Stadium","city":"Kansas City"},
    # ── GROUP K ───────────────────────────────────────────────────────────
    {"group":"K","team1":"Portugal","team2":"DR Congo","date":"Jun 17","time":"1:00 PM ET","venue":"NRG Stadium","city":"Houston"},
    {"group":"K","team1":"Uzbekistan","team2":"Colombia","date":"Jun 17","time":"10:00 PM ET","venue":"Estadio Azteca","city":"Mexico City"},
    {"group":"K","team1":"Portugal","team2":"Uzbekistan","date":"Jun 23","time":"1:00 PM ET","venue":"NRG Stadium","city":"Houston"},
    {"group":"K","team1":"Colombia","team2":"DR Congo","date":"Jun 23","time":"10:00 PM ET","venue":"Estadio Akron","city":"Guadalajara"},
    {"group":"K","team1":"Colombia","team2":"Portugal","date":"Jun 27","time":"7:30 PM ET","venue":"Hard Rock Stadium","city":"Miami"},
    {"group":"K","team1":"DR Congo","team2":"Uzbekistan","date":"Jun 27","time":"7:30 PM ET","venue":"Mercedes-Benz Stadium","city":"Atlanta"},
    # ── GROUP L ───────────────────────────────────────────────────────────
    {"group":"L","team1":"England","team2":"Croatia","date":"Jun 17","time":"4:00 PM ET","venue":"AT&T Stadium","city":"Dallas"},
    {"group":"L","team1":"Ghana","team2":"Panama","date":"Jun 17","time":"7:00 PM ET","venue":"BMO Field","city":"Toronto"},
    {"group":"L","team1":"England","team2":"Ghana","date":"Jun 23","time":"4:00 PM ET","venue":"Gillette Stadium","city":"Boston"},
    {"group":"L","team1":"Panama","team2":"Croatia","date":"Jun 23","time":"7:00 PM ET","venue":"BMO Field","city":"Toronto"},
    {"group":"L","team1":"Panama","team2":"England","date":"Jun 27","time":"5:00 PM ET","venue":"MetLife Stadium","city":"New York/NJ"},
    {"group":"L","team1":"Croatia","team2":"Ghana","date":"Jun 27","time":"5:00 PM ET","venue":"Lincoln Financial Field","city":"Philadelphia"},
]

# ── ROUND OF 32 (locked tournament bracket) ─────────────────────────────────
WC_ROUND_OF_32 = [
    {"slot":"M1","team1":"South Africa","team2":"Canada","date":"June 28","time":"3:00 PM ET","venue":"SoFi Stadium","city":"Inglewood"},
    {"slot":"M2","team1":"Brazil","team2":"Japan","date":"June 29","time":"12:00 PM ET","venue":"NRG Stadium","city":"Houston"},
    {"slot":"M3","team1":"Germany","team2":"Paraguay","date":"June 29","time":"3:00 PM ET","venue":"Gillette Stadium","city":"Foxborough"},
    {"slot":"M4","team1":"Netherlands","team2":"Morocco","date":"June 29","time":"9:00 PM ET","venue":"Estadio Monterrey","city":"Monterrey"},
    {"slot":"M5","team1":"Ivory Coast","team2":"Norway","date":"June 30","time":"12:00 PM ET","venue":"AT&T Stadium","city":"Arlington"},
    {"slot":"M6","team1":"France","team2":"Sweden","date":"June 30","time":"3:00 PM ET","venue":"MetLife Stadium","city":"East Rutherford"},
    {"slot":"M7","team1":"Mexico","team2":"Ecuador","date":"June 30","time":"9:00 PM ET","venue":"Estadio Azteca","city":"Mexico City"},
    {"slot":"M8","team1":"England","team2":"DR Congo","date":"July 1","time":"12:00 PM ET","venue":"Mercedes-Benz Stadium","city":"Atlanta"},
    {"slot":"M9","team1":"Belgium","team2":"Senegal","date":"July 1","time":"4:00 PM ET","venue":"Lumen Field","city":"Seattle"},
    {"slot":"M10","team1":"United States","team2":"Bosnia-Herzegovina","date":"July 1","time":"8:00 PM ET","venue":"Levi's Stadium","city":"Santa Clara"},
    {"slot":"M11","team1":"Spain","team2":"Austria","date":"July 2","time":"3:00 PM ET","venue":"SoFi Stadium","city":"Inglewood"},
    {"slot":"M12","team1":"Switzerland","team2":"Algeria","date":"July 2","time":"11:00 PM ET","venue":"Vancouver Stadium","city":"Vancouver"},
    {"slot":"M13","team1":"Portugal","team2":"Croatia","date":"July 2","time":"7:00 PM ET","venue":"Toronto Stadium","city":"Toronto"},
    {"slot":"M14","team1":"Australia","team2":"Egypt","date":"July 3","time":"2:00 PM ET","venue":"AT&T Stadium","city":"Arlington"},
    {"slot":"M15","team1":"Argentina","team2":"Cape Verde","date":"July 3","time":"6:00 PM ET","venue":"Hard Rock Stadium","city":"Miami Gardens"},
    {"slot":"M16","team1":"Colombia","team2":"Ghana","date":"July 3","time":"9:30 PM ET","venue":"Arrowhead Stadium","city":"Kansas City"},
]

ROUND_OF_16_PAIRS = [
    ("M3","M6"), ("M1","M4"), ("M13","M11"), ("M10","M9"),
    ("M2","M5"), ("M7","M8"), ("M15","M14"), ("M12","M16"),
]

# R16 → QF → SF → Final adjacency (Left side = M1,M3,M4,M6,M9,M10,M11,M13 / Right side = M2,M5,M7,M8,M12,M14,M15,M16)
BRACKET_ADVANCE = {
    "R16_1": ("M3","M6"), "R16_2": ("M1","M4"),
    "R16_3": ("M13","M11"), "R16_4": ("M10","M9"),
    "R16_5": ("M2","M5"), "R16_6": ("M7","M8"),
    "R16_7": ("M15","M14"), "R16_8": ("M12","M16"),
    "QF_1": ("R16_1","R16_2"), "QF_2": ("R16_3","R16_4"),
    "QF_3": ("R16_5","R16_6"), "QF_4": ("R16_7","R16_8"),
    "SF_1": ("QF_1","QF_2"), "SF_2": ("QF_3","QF_4"),
    "FINAL": ("SF_1","SF_2"),
}


# ── HEAD TO HEAD HISTORY ──────────────────────────────────────────────────
H2H = {
    frozenset(["Argentina","France"]):[{"year":2018,"round":"R16","score":"4-3","winner":"France","note":"Mbappé's breakout — scored twice at 19"},{"year":1930,"round":"Group","score":"1-0","winner":"France","note":"First WC meeting between the two nations"}],
    frozenset(["England","Germany"]):[{"year":2010,"round":"R16","score":"4-1","winner":"Germany","note":"Lampard's ghost goal — ball clearly crossed the line"},{"year":1966,"round":"Final","score":"4-2","winner":"England","note":"England's only WC title — Geoff Hurst hat-trick"}],
    frozenset(["Brazil","France"]):[{"year":2006,"round":"QF","score":"1-0","winner":"France","note":"Zidane masterclass — ended Ronaldo's last great tournament"},{"year":1998,"round":"Final","score":"3-0","winner":"France","note":"France on home soil — Zidane scored twice"}],
    frozenset(["Germany","Brazil"]):[{"year":2014,"round":"SF","score":"7-1","winner":"Germany","note":"The Mineirazo — Brazil's greatest sporting humiliation"},{"year":2002,"round":"Final","score":"2-0","winner":"Brazil","note":"Ronaldo's redemption — scored both goals"}],
    frozenset(["Argentina","England"]):[{"year":1986,"round":"QF","score":"2-1","winner":"Argentina","note":"Hand of God + Goal of the Century — Maradona's finest hour"},{"year":1998,"round":"R16","score":"2-2 (4-3p)","winner":"Argentina","note":"Beckham red card, Owen wonder goal"},{"year":2002,"round":"Group","score":"1-0","winner":"England","note":"Beckham penalty redemption"}],
    frozenset(["Netherlands","Argentina"]):[{"year":2022,"round":"QF","score":"2-2 (4-3p)","winner":"Argentina","note":"18 yellow cards — Messi vs Van Gaal feud exploded"},{"year":1978,"round":"Final","score":"3-1 AET","winner":"Argentina","note":"Argentina's first World Cup on home soil"}],
    frozenset(["Morocco","Spain"]):[{"year":2022,"round":"R16","score":"0-0 (3-0p)","winner":"Morocco","note":"Bono saved 3 penalties — Spain humiliated"},{"year":1998,"round":"Group","score":"3-2","winner":"Spain","note":"Last-gasp Spain winner in a classic"}],
    frozenset(["Morocco","Portugal"]):[{"year":2022,"round":"QF","score":"1-0","winner":"Morocco","note":"En-Nesyri header — Africa's first ever WC semi-final"}],
    frozenset(["France","Croatia"]):[{"year":2018,"round":"Final","score":"4-2","winner":"France","note":"Mbappé youngest scorer in WC final since Pelé"},{"year":1998,"round":"SF","score":"2-1","winner":"France","note":"Thuram scored twice — only goals of his entire career"}],
    frozenset(["Germany","Argentina"]):[{"year":2014,"round":"Final","score":"1-0 AET","winner":"Germany","note":"Götze winner — Germany's 4th World Cup title"},{"year":1990,"round":"Final","score":"1-0","winner":"Germany","note":"Controversial Sensini penalty — Maradona wept"},{"year":1986,"round":"Final","score":"3-2","winner":"Argentina","note":"Maradona's tournament — Burruchaga winner"}],
    frozenset(["USA","England"]):[{"year":2022,"round":"Group","score":"0-0","winner":"Draw","note":"Pulisic's USA held England in a famous stalemate"},{"year":1950,"round":"Group","score":"1-0","winner":"USA","note":"Biggest WC upset in history at the time"}],
    frozenset(["South Korea","Germany"]):[{"year":2018,"round":"Group","score":"2-0","winner":"South Korea","note":"Defending champions Germany eliminated — shock of the tournament"}],
    frozenset(["Saudi Arabia","Argentina"]):[{"year":2022,"round":"Group","score":"2-1","winner":"Saudi Arabia","note":"Greatest WC upset of the modern era — Messi stunned"}],
    frozenset(["Japan","Germany"]):[{"year":2022,"round":"Group","score":"2-1","winner":"Japan","note":"Japan's comeback win shocked the world"}],
    frozenset(["Japan","Spain"]):[{"year":2022,"round":"Group","score":"2-1","winner":"Japan","note":"Japan completed the double — beat Spain AND Germany"}],
    frozenset(["Norway","Argentina"]):[{"year":1994,"round":"Group","score":"1-0","winner":"Norway","note":"Norway's only WC meeting — stunned Maradona's Argentina"}],
    frozenset(["Brazil","Argentina"]):[{"year":1990,"round":"R16","score":"1-0","winner":"Argentina","note":"Last WC Clásico — Caniggia goal sealed it"},{"year":1982,"round":"Group","score":"3-1","winner":"Brazil","note":"Classic South American battle"}],
    frozenset(["Senegal","England"]):[{"year":2022,"round":"R16","score":"3-0","winner":"England","note":"Henderson, Saka, Kane — England's most comfortable WC win"}],
}

# ── DARK HORSE ────────────────────────────────────────────────────────────
DARK_HORSES = {
    "NOR":{"flag":"🇳🇴","tagline":"The Haaland Factor","story":"Norway has never won a WC match in modern football — but they've also never had Erling Haaland. The Golden Boot winner is the most dangerous striker alive. Add Ødegaard orchestrating from midfield and Norway could be the biggest story of Group I.","stat":"Haaland scored 88.0 in our system — highest striker since Kane"},
    "CIV":{"flag":"🇨🇮","tagline":"The New Generation","story":"Forget the Drogba era. Amad Diallo (Man United), Evan N'Dicka (Roma), and Simon Adingra (Monaco) lead a young, electric Ivory Coast squad built for the counter-attack. Group E is tough, but Les Éléphants have made a habit of upsetting favourites.","stat":"Average age: 24.3 — one of the youngest squads in the tournament"},
    "MAR":{"flag":"🇲🇦","tagline":"Unfinished Business","story":"Not a dark horse — they're a proven quantity. Morocco reached the 2022 semi-finals and they're back with Hakimi, Ezzalzouli, Amrabat and Bounou. Anyone calling them a dark horse clearly wasn't watching Qatar 2022.","stat":"Only team outside Europe/South America to reach WC semis since 2002"},
    "JPN":{"flag":"🇯🇵","tagline":"Giant Killers on Repeat","story":"In 2022, Japan beat Germany AND Spain in the same group. In 2026, Kubo (Real Sociedad), Kamada (Crystal Palace) and Endo (Liverpool) lead a squad built on ferocious pressing. Ask Germany. Oh wait — they can't answer, they're already eliminated.","stat":"Japan knocked out 2 of the last 3 WC winners in 2022"},
    "NOR_backup":"",
    "CAN":{"flag":"🇨🇦","tagline":"Home Field Advantage","story":"Playing at home for the first time since 1986. Jonathan David (Juventus) and Alphonso Davies (Bayern Munich) are legitimate world-class. The crowd noise at BMO Field will be deafening. Host nation energy is real — and Canada is ready to shock.","stat":"Jonathan David scored 25+ goals in Europe this season"},
}

THE_DARK_HORSE = "NOR"  # computed: highest talent score outside top-8 FIFA nations

def clean_html(s):
    return "\n".join(l.strip() for l in s.split("\n"))

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp{font-family:'Plus Jakarta Sans',-apple-system,sans-serif;}
.stApp{background-color:#061a06;background-image:repeating-linear-gradient(0deg,transparent,transparent 59px,rgba(255,255,255,0.02) 60px),repeating-linear-gradient(90deg,transparent,transparent 59px,rgba(255,255,255,0.02) 60px);background-size:60px 60px;}
section[data-testid="stSidebar"]{display:none;}

/* Top nav tabs */
.stTabs [data-baseweb="tab-list"]{gap:2px;background:rgba(5,20,5,0.9);border-radius:12px;padding:6px;border:1px solid rgba(74,222,128,0.15);backdrop-filter:blur(12px);width:100%;display:flex;}
.stTabs [data-baseweb="tab"]{background:transparent;border-radius:8px;color:#86efac;font-weight:600;font-size:0.88rem;padding:10px 0;border:none;transition:all 0.2s;flex:1;text-align:center;}
.stTabs [data-baseweb="tab"]:hover{background:rgba(74,222,128,0.08);color:#4ade80;}
.stTabs [aria-selected="true"]{background:rgba(74,222,128,0.15)!important;color:#4ade80!important;border:1px solid rgba(74,222,128,0.3)!important;}
.stTabs [data-baseweb="tab-highlight"]{display:none;}
.stTabs [data-baseweb="tab-border"]{display:none;}

/* KPI cards */
.kpi-box{background:rgba(8,32,8,0.85);border:1px solid rgba(74,222,128,0.18);border-radius:14px;padding:20px 22px;margin:6px 0;transition:all 0.3s ease;}
.kpi-box:hover{border-color:rgba(74,222,128,0.35);transform:translateY(-2px);}
.kpi-label{font-size:0.75rem;color:#86efac;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:6px;}
.kpi-val{font-size:2rem;font-weight:800;background:linear-gradient(90deg,#4ade80,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;}
.kpi-sub{font-size:0.72rem;color:#4b7c4b;margin-top:4px;font-weight:500;}

/* Player cards */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;margin-top:16px;}
.pcard{background:rgba(8,28,8,0.85);border:1px solid rgba(74,222,128,0.12);border-radius:14px;padding:22px;transition:all 0.3s;position:relative;overflow:hidden;}
.pcard::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(180deg,#4ade80,#16a34a);}
.pcard:hover{transform:translateY(-5px);border-color:rgba(74,222,128,0.3);}
.pname{font-size:1.15rem;font-weight:700;color:#f0fdf4;margin:0;}
.psub{font-size:0.82rem;color:#86efac;margin:4px 0 12px;opacity:0.8;}
.pbadge{background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.25);color:#4ade80;padding:3px 9px;border-radius:9999px;font-size:0.7rem;font-weight:600;display:inline-block;}
.pstats{display:grid;grid-template-columns:1fr 1fr;gap:6px 10px;margin-top:14px;font-size:0.82rem;border-top:1px solid rgba(74,222,128,0.08);padding-top:12px;}
.plabel{color:#4b7c4b;}
.pval{color:#dcfce7;font-weight:600;text-align:right;}
.pscore{font-size:1.5rem;font-weight:800;background:linear-gradient(135deg,#4ade80,#16a34a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:right;}

/* Titles */
.page-title{font-size:2.4rem;font-weight:800;background:linear-gradient(90deg,#fbbf24,#4ade80,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px;letter-spacing:-0.02em;}
.page-sub{color:#86efac;font-size:1rem;margin-bottom:24px;opacity:0.75;}

/* Match card */
.match-hdr{background:linear-gradient(135deg,rgba(8,32,8,0.95),rgba(3,12,3,0.98));border:1px solid rgba(74,222,128,0.2);border-radius:18px;padding:36px;text-align:center;margin:16px 0;}
.match-team{font-size:2.2rem;font-weight:800;color:#f0fdf4;}
.match-vs{font-size:1.3rem;font-weight:700;color:#fbbf24;padding:0 20px;}
.mpill{display:inline-flex;align-items:center;gap:5px;background:rgba(8,32,8,0.8);border:1px solid rgba(74,222,128,0.15);color:#86efac;padding:5px 14px;border-radius:9999px;font-size:0.8rem;font-weight:500;margin:3px;}
.storyline{background:rgba(8,28,8,0.7);border:1px solid rgba(74,222,128,0.15);border-left:4px solid #4ade80;border-radius:14px;padding:28px 32px;margin:16px 0;line-height:1.9;font-size:1.05rem;color:#dcfce7;}
.gem-box{background:rgba(251,191,36,0.06);border:1px solid rgba(251,191,36,0.25);border-left:4px solid #fbbf24;border-radius:14px;padding:20px 24px;margin:12px 0;}
.star-box{background:rgba(8,28,8,0.7);border:1px solid rgba(74,222,128,0.1);border-radius:14px;padding:24px;text-align:center;}
.star-num{font-size:3rem;font-weight:800;color:#f0fdf4;line-height:1;}
.mini-row{display:flex;justify-content:space-between;align-items:center;padding:9px 12px;border-bottom:1px solid rgba(74,222,128,0.05);border-radius:7px;margin-bottom:3px;background:rgba(3,12,3,0.5);}
.mini-row:hover{background:rgba(74,222,128,0.06);}

/* Schedule */
.sched-group{background:rgba(8,28,8,0.7);border:1px solid rgba(74,222,128,0.1);border-radius:14px;padding:16px 20px;margin-bottom:14px;}
.sched-match{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(74,222,128,0.05);}
.sched-match:last-child{border-bottom:none;}
.sched-teams{font-weight:700;color:#f0fdf4;font-size:0.95rem;}
.sched-meta{font-size:0.8rem;color:#86efac;opacity:0.7;}
.sched-date{font-size:0.82rem;color:#4ade80;font-weight:600;}

/* Prob bar */
.prob-bar-wrap{background:rgba(5,15,5,0.6);border-radius:9999px;height:10px;margin:8px 0;overflow:hidden;}
.prob-bar-fill{height:100%;border-radius:9999px;transition:width 0.6s ease;}

/* Comparison table */
.ctable{width:100%;border-collapse:collapse;margin-top:16px;background:rgba(5,18,5,0.6);border-radius:12px;border:1px solid rgba(74,222,128,0.1);overflow:hidden;}
.ctable th{padding:12px 16px;color:#86efac;font-weight:600;text-align:left;background:rgba(8,32,8,0.8);border-bottom:2px solid rgba(74,222,128,0.15);}
.ctable td{padding:10px 16px;border-bottom:1px solid rgba(74,222,128,0.05);color:#dcfce7;}

/* Knockout bracket */
.ko-card{background:rgba(8,28,8,0.85);border:1px solid rgba(74,222,128,0.15);border-radius:14px;padding:18px 20px;margin-bottom:12px;transition:all 0.25s;}
.ko-card:hover{border-color:rgba(74,222,128,0.3);transform:translateY(-2px);}
.ko-card.played{border-color:rgba(74,222,128,0.35);background:rgba(8,32,8,0.95);}
.ko-slot{font-size:0.65rem;color:#4ade80;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;margin-bottom:8px;}
.ko-teams{font-size:1rem;font-weight:700;color:#f0fdf4;margin-bottom:10px;line-height:1.5;}
.ko-meta{font-size:0.75rem;color:#86efac;opacity:0.75;margin-bottom:12px;}
.ko-badge{display:inline-block;background:rgba(251,191,36,0.12);border:1px solid rgba(251,191,36,0.35);color:#fbbf24;padding:4px 12px;border-radius:9999px;font-size:0.78rem;font-weight:700;margin-top:6px;}
.ko-badge.actual{background:rgba(74,222,128,0.12);border-color:rgba(74,222,128,0.35);color:#4ade80;}
.ko-score{font-size:1.4rem;font-weight:900;color:#f0fdf4;margin:8px 0;}
.bracket-col{background:rgba(5,18,5,0.5);border:1px solid rgba(74,222,128,0.08);border-radius:14px;padding:14px;margin-bottom:12px;}
.bracket-round{font-size:0.72rem;color:#4ade80;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;margin-bottom:10px;text-align:center;}
.bracket-match{background:rgba(8,28,8,0.7);border:1px solid rgba(74,222,128,0.1);border-radius:10px;padding:10px 12px;margin-bottom:8px;font-size:0.82rem;}
.bracket-team{color:#f0fdf4;font-weight:600;}
.bracket-team.winner{color:#4ade80;}
.bracket-tbd{color:#4b7c4b;font-style:italic;}
</style>
""", unsafe_allow_html=True)

# ── HERO BANNER ───────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:26px 32px 20px;border-bottom:1px solid rgba(74,222,128,0.12);margin-bottom:8px;text-align:center;">
    <div style="font-size:0.68rem;color:#4ade80;text-transform:uppercase;letter-spacing:0.25em;font-weight:700;margin-bottom:10px;">⚽ Kickoff 26</div>
    <div style="font-size:2.4rem;font-weight:900;color:#f0fdf4;letter-spacing:0.01em;line-height:1.15;margin-bottom:6px;">
        Road to the FIFA World Cup <span style="color:#4ade80;">26</span>
    </div>
    <div style="font-size:0.95rem;color:#86efac;font-weight:400;letter-spacing:0.02em;margin-bottom:16px;opacity:0.8;">
        Your guide to the 2026 World Cup.
    </div>
    <div style="display:flex;justify-content:center;align-items:center;gap:12px;">
        <div style="height:1px;width:80px;background:rgba(74,222,128,0.2);"></div>
        <span style="font-size:0.72rem;font-weight:800;color:#4ade80;letter-spacing:0.15em;text-transform:uppercase;">48 Nations</span>
        <div style="width:4px;height:4px;border-radius:50%;background:#fbbf24;"></div>
        <span style="font-size:0.72rem;font-weight:800;color:#fbbf24;letter-spacing:0.15em;text-transform:uppercase;">1 Winner</span>
        <div style="height:1px;width:80px;background:rgba(74,222,128,0.2);"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LIVE / NEXT MATCH IN HERO ─────────────────────────────────────────────
import re as _re_hero
from datetime import timedelta as _td
from datetime import timedelta

# Month name to number map for schedule dates like "Jun 13"
_MONTH_MAP = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
              "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

def _parse_match_utc(m):
    """Parse match ET time to UTC datetime. EDT = UTC-4"""
    try:
        ts = _re_hero.search(r"(\d+):(\d+)\s*(AM|PM)", m.get("time",""))
        if not ts: return None, None
        hh=int(ts.group(1)); mm=int(ts.group(2)); ap=ts.group(3)
        if ap=="PM" and hh!=12: hh+=12
        if ap=="AM" and hh==12: hh=0
        # Parse date like "Jun 13" -> month/day, year always 2026
        parts = m["date"].split()
        mon = _MONTH_MAP.get(parts[0], 6)
        day = int(parts[1])
        # ET is UTC-4 (EDT in June) so add 4 hours to convert to UTC
        start_utc = datetime(2026, mon, day, hh, mm, 0, tzinfo=timezone.utc) + timedelta(hours=4)
        end_utc = start_utc + timedelta(hours=2)  # assume 2hr match window
        return start_utc, end_utc
    except:
        return None, None

def _get_hero_banner():
    try:
        _ls = fetch_live_scores()
    except:
        _ls = {}
    _now = datetime.now(timezone.utc)
    _live_m = None; _next_m = None; _next_start = None

    # Sort schedule by actual UTC time so we always get the real next match
    def _sort_key(m):
        s = _parse_match_utc(m)
        return s if s else datetime(2099,1,1,tzinfo=timezone.utc)

    for _m in sorted(WC_SCHEDULE, key=_sort_key):
        _start, _end = _parse_match_utc(_m)
        if _start is None: continue
        _s1,_s2,_,_ = get_match_score(_m["team1"],_m["team2"],_ls)
        # If scored by API → definitely finished
        if _s1 is not None: continue
        # If ended more than 30 mins ago → assume finished even if no API score yet
        if _end < _now - timedelta(minutes=30): continue
        # Live: within match window
        if _start <= _now <= _end and _live_m is None:
            _live_m = _m
        # Next: starts in the future, pick the soonest
        if _now < _start and (_next_m is None or _start < _next_start):
            _next_m = _m
            _next_start = _start
    return _live_m, _next_m, _ls

try:
    _live_m, _next_m, _ls = _get_hero_banner()
except Exception as _e:
    st.error(f"Banner error: {_e}")
    _live_m, _next_m, _ls = None, None, {}

_bm = _live_m if _live_m else _next_m

if _bm:
    _ft1 = FLAGS.get(NATION_TO_CODE.get(_bm["team1"],""),"")
    _ft2 = FLAGS.get(NATION_TO_CODE.get(_bm["team2"],""),"")
    if _live_m:
        # Show LIVE banner
        st.markdown(clean_html(f'''<div style="background:linear-gradient(135deg,rgba(40,5,5,0.97),rgba(20,2,2,0.99));border:1px solid rgba(239,68,68,0.4);border-radius:16px;padding:20px 32px;margin-bottom:12px;text-align:center;">
            <div style="font-size:0.68rem;color:#ef4444;text-transform:uppercase;letter-spacing:0.25em;font-weight:700;margin-bottom:8px;">🔴 &nbsp; Live Now</div>
            <div style="font-size:1.6rem;font-weight:900;color:#f0fdf4;">{_ft1} {_bm["team1"]} <span style="color:#5a2020;font-size:1rem;padding:0 10px;">vs</span> {_bm["team2"]} {_ft2}</div>
            <div style="font-size:0.75rem;color:#fca5a5;margin-top:8px;">{_bm.get("venue","")} &nbsp;·&nbsp; {_bm.get("city","")} &nbsp;·&nbsp; {_bm.get("time","")}</div>
        </div>'''), unsafe_allow_html=True)
    else:
        # Show next match countdown
        try:
            _ts2 = _re_hero.search(r"(\d+):(\d+)\s*(AM|PM)", _bm.get("time",""))
            if _ts2:
                _h2=int(_ts2.group(1)); _m2=int(_ts2.group(2)); _a2=_ts2.group(3)
                if _a2=="PM" and _h2!=12: _h2+=12
                if _a2=="AM" and _h2==12: _h2=0
                _dp2=_bm["date"].split("-")
                _tms=int((datetime(int(_dp2[0]),int(_dp2[1]),int(_dp2[2]),_h2,_m2,0,tzinfo=timezone.utc)+_td(hours=5)).timestamp()*1000)
            else: _tms=0
        except: _tms=0
        _hero_html = (
            "<!DOCTYPE html><html><body style='margin:0;padding:0;background:#061a06;'>"
            "<div style='background:linear-gradient(135deg,rgba(8,28,8,0.97),rgba(3,10,3,0.99));border:1px solid rgba(74,222,128,0.2);border-radius:16px;padding:20px 32px;text-align:center;'>"
            "<div style='font-size:0.65rem;color:#4ade80;text-transform:uppercase;letter-spacing:0.22em;font-weight:700;margin-bottom:8px;'>Next Match</div>"
            f"<div style='font-size:1.5rem;font-weight:900;color:#f0fdf4;margin-bottom:4px;'>{_ft1} {_bm['team1']} <span style='color:#4b7c4b;font-size:1rem;padding:0 8px;'>vs</span> {_bm['team2']} {_ft2}</div>"
            f"<div style='font-size:0.72rem;color:#86efac;margin-bottom:12px;'>{_bm['date']} &nbsp;·&nbsp; {_bm['time']} &nbsp;·&nbsp; {_bm['city']}</div>"
            "<div id='hero-timer' style='font-size:2.2rem;font-weight:900;color:#fbbf24;font-variant-numeric:tabular-nums;'>--</div>"
            "</div>"
            "</body></html>"
        )
        st.components.v1.html(_hero_html, height=90)

# ── LOAD DATA ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists("master_players_v2.csv"):
        st.error("⚠️ master_players_v2.csv not found. Run clean_football_data.py first.")
        st.stop()
    df = pd.read_csv("master_players_v2.csv")
    df["Hidden_Gem"] = df["Hidden_Gem"].astype(bool)
    df["WC_Watchlist_V2"] = df["WC_Watchlist_V2"].astype(bool)
    for col in ["Attacker_Index","Creator_Index","Defensive_Index","Gls_p90","Ast_p90","Int_p90"]:
        df[col+"_Pct"] = (df[col].rank(pct=True)*100).round(1)
    return df

df = load_data()

# ── HELPERS ───────────────────────────────────────────────────────────────
def kpi(label, val, sub=None):
    sub_h = f'<div class="kpi-sub">{sub}</div>' if sub else ''
    return f'<div class="kpi-box"><div class="kpi-label">{label}</div><div class="kpi-val">{val}</div>{sub_h}</div>'

def score_color(s):
    if s >= 80: return "#4ade80"
    elif s >= 60: return "#fbbf24"
    elif s >= 40: return "#fb923c"
    else: return "#f87171"

def get_intensity(avg):
    if avg >= 85:   return "🏆 Wouldn't Miss For The World","#EF4444","rgba(239,68,68,0.15)"
    elif avg >= 70: return "🔥 Must Watch","#F97316","rgba(249,115,22,0.15)"
    elif avg >= 50: return "👀 Worth Watching","#EAB308","rgba(234,179,8,0.15)"
    else:           return "🌱 Low Intensity","#22c55e","rgba(34,197,94,0.15)"

def team_avg(code):
    p = df[df["Nation"]==code].sort_values("Overall_Index",ascending=False).head(5)["Overall_Index"].tolist()
    return np.mean(p) if p else 15.0

def win_probability(team1, team2):
    """Blend scouting score (60%) with FIFA ranking (40%)"""
    c1 = NATION_TO_CODE.get(team1,""); c2 = NATION_TO_CODE.get(team2,"")
    # Score component
    s1 = team_avg(c1); s2 = team_avg(c2)
    score_total = s1 + s2
    sp1 = s1/score_total if score_total>0 else 0.5
    # FIFA ranking component (lower rank = better)
    r1 = FIFA_RANKINGS.get(c1, 50); r2 = FIFA_RANKINGS.get(c2, 50)
    rank_total = (1/r1) + (1/r2)
    rp1 = (1/r1)/rank_total if rank_total>0 else 0.5
    # Blend
    raw1 = sp1*0.60 + rp1*0.40
    raw2 = 1 - raw1
    # Add draw probability (reduce both by 15-20% based on closeness)
    gap = abs(raw1 - raw2)
    draw_prob = max(0.10, 0.28 - gap*0.5)
    p1 = raw1 * (1 - draw_prob)
    p2 = raw2 * (1 - draw_prob)
    return round(p1*100,1), round(draw_prob*100,1), round(p2*100,1)

def knockout_predict(team1, team2):
    """Knockout win% — redistributes draw probability proportionally."""
    wp1, wpd, wp2 = win_probability(team1, team2)
    total = wp1 + wp2
    adj1 = wp1 + wpd * (wp1/total if total>0 else 0.5)
    adj2 = wp2 + wpd * (wp2/total if total>0 else 0.5)
    predicted_winner = team1 if adj1 >= adj2 else team2
    return predicted_winner, round(adj1, 1), round(adj2, 1)

_KO_DATE_ORDER = {
    "June 28": 0, "June 29": 1, "June 30": 2,
    "July 1": 3, "July 2": 4, "July 3": 5,
}

def _parse_ko_date_utc(match):
    """Parse knockout date + time to UTC. Uses same logic as _parse_match_utc."""
    return _parse_match_utc(match)[0] or datetime(2099, 1, 1, tzinfo=timezone.utc)

def _ko_flag(team):
    return FLAGS.get(NATION_TO_CODE.get(team, ""), "⚽")

def get_round_of_32_data():
    """Return the hardcoded Round of 32 matchups list."""
    return WC_ROUND_OF_32

def _pretty_feed_label(feed_id):
    """Convert a feed id like 'M3', 'R16_1', 'QF_1', 'SF_1' into a clean,
    human-readable placeholder label for unplayed bracket slots."""
    if feed_id.startswith("M"):
        return f"Winner · Match {feed_id[1:]}"
    if feed_id.startswith("R16_"):
        return f"Winner · R16 #{feed_id.split('_')[1]}"
    if feed_id.startswith("QF_"):
        return f"Winner · QF{feed_id.split('_')[1]}"
    if feed_id.startswith("SF"):
        n = feed_id.replace("SF_", "").replace("SF", "")
        return f"Winner · SF{n}"
    return f"Winner · {feed_id}"

def _resolve_match(t1, t2, live_scores):
    """
    Single source of truth for resolving a knockout match's state.
    Returns (is_finished, winner, score_str, s1, s2, is_live).

    Fixes two bugs from the previous per-block duplicated logic:
    1. A tied full-time score with no ET/penalty data was previously
       defaulting to "t2 wins" (since s1_ft > s2_ft was False). Now a
       tie with no decisive data correctly stays unresolved (is_finished=False).
    2. "Live" was previously guessed purely from the match date matching
       today, even if kickoff hadn't happened yet. Now it's only flagged
       live when the API actually shows in-progress signal (half-time
       score or recorded goals) with no full-time result yet.
    """
    s1, s2, _, _ = get_match_score(t1, t2, live_scores)

    match_data = None
    reversed_key = False
    for k in [f"{t1}|{t2}", f"{t2}|{t1}"]:
        if k in live_scores:
            match_data = live_scores[k]
            reversed_key = (k == f"{t2}|{t1}")
            break

    if s1 is None:
        is_live = False
        if match_data:
            ht = match_data.get("ht")
            g1 = match_data.get("goals1") or []
            g2 = match_data.get("goals2") or []
            if ht is not None or g1 or g2:
                is_live = True
        return False, None, None, None, None, is_live

    p = match_data.get("p") if match_data else None
    et = match_data.get("et") if match_data else None
    s1_ft, s2_ft = (s2, s1) if reversed_key else (s1, s2)

    if p is not None:
        s1_p, s2_p = (p[1], p[0]) if reversed_key else (p[0], p[1])
        winner = t1 if s1_p > s2_p else t2
        return True, winner, f"{s1_ft}\u2013{s2_ft} ({s1_p}\u2013{s2_p} pen)", s1, s2, False
    elif et is not None:
        s1_et, s2_et = (et[1], et[0]) if reversed_key else (et[0], et[1])
        winner = t1 if s1_et > s2_et else t2
        return True, winner, f"{s1_et}\u2013{s2_et} AET", s1, s2, False
    elif s1_ft != s2_ft:
        winner = t1 if s1_ft > s2_ft else t2
        return True, winner, f"{s1_ft}\u2013{s2_ft}", s1, s2, False
    else:
        # Tied at full time, no ET/penalty data yet -- still pending, not finished
        return False, None, f"{s1_ft}\u2013{s2_ft} (ET/pens pending)", s1, s2, True

def get_bracket_data(live_scores):
    # R32
    r32 = {}
    for m in WC_ROUND_OF_32:
        slot = m["slot"]
        t1, t2 = m["team1"], m["team2"]
        is_finished, winner, score_str, s1, s2, is_live = _resolve_match(t1, t2, live_scores)

        r32[slot] = {
            "team1": t1,
            "team2": t2,
            "score1": s1,
            "score2": s2,
            "winner": winner,
            "is_finished": is_finished,
            "is_live": is_live,
            "score_str": score_str,
            "date": m["date"],
            "venue": m["venue"],
            "city": m["city"]
        }
        
    # R16
    r16_slots = {
        "R16_1": ("M3", "M6"),
        "R16_2": ("M1", "M4"),
        "R16_3": ("M13", "M11"),
        "R16_4": ("M10", "M9"),
        "R16_5": ("M2", "M5"),
        "R16_6": ("M7", "M8"),
        "R16_7": ("M15", "M14"),
        "R16_8": ("M12", "M16"),
    }
    
    r16 = {}
    for slot_id, (feed_a, feed_b) in r16_slots.items():
        fa, fb = r32[feed_a], r32[feed_b]
        t1 = fa["winner"] if fa["is_finished"] else None
        t2 = fb["winner"] if fb["is_finished"] else None

        is_finished, winner, score_str, s1, s2, _ = (False, None, None, None, None, False)
        if t1 and t2:
            is_finished, winner, score_str, s1, s2, _ = _resolve_match(t1, t2, live_scores)

        # Show the real "Team A or Team B" options from the feeder match instead
        # of a generic placeholder, since both candidates are already known.
        label1 = f"{fa['team1']} or {fa['team2']}" if not fa["is_finished"] else _pretty_feed_label(feed_a)
        label2 = f"{fb['team1']} or {fb['team2']}" if not fb["is_finished"] else _pretty_feed_label(feed_b)

        r16[slot_id] = {
            "team1": t1,
            "team2": t2,
            "score1": s1,
            "score2": s2,
            "winner": winner,
            "is_finished": is_finished,
            "is_live": False,
            "score_str": score_str,
            "label1": label1,
            "label2": label2
        }
        
    # QF
    qf_slots = {
        "QF_1": ("R16_1", "R16_2"),
        "QF_2": ("R16_3", "R16_4"),
        "QF_3": ("R16_5", "R16_6"),
        "QF_4": ("R16_7", "R16_8"),
    }
    
    qf = {}
    for slot_id, (feed_a, feed_b) in qf_slots.items():
        fa, fb = r16[feed_a], r16[feed_b]
        t1 = fa["winner"] if fa["is_finished"] else None
        t2 = fb["winner"] if fb["is_finished"] else None

        is_finished, winner, score_str, s1, s2, _ = (False, None, None, None, None, False)
        if t1 and t2:
            is_finished, winner, score_str, s1, s2, _ = _resolve_match(t1, t2, live_scores)

        qf[slot_id] = {
            "team1": t1,
            "team2": t2,
            "score1": s1,
            "score2": s2,
            "winner": winner,
            "is_finished": is_finished,
            "is_live": False,
            "score_str": score_str,
            "label1": _pretty_feed_label(feed_a),
            "label2": _pretty_feed_label(feed_b)
        }
        
    # SF
    sf_slots = {
        "SF_1": ("QF_1", "QF_2"),
        "SF_2": ("QF_3", "QF_4"),
    }
    
    sf = {}
    for slot_id, (feed_a, feed_b) in sf_slots.items():
        fa, fb = qf[feed_a], qf[feed_b]
        t1 = fa["winner"] if fa["is_finished"] else None
        t2 = fb["winner"] if fb["is_finished"] else None

        is_finished, winner, score_str, s1, s2, _ = (False, None, None, None, None, False)
        if t1 and t2:
            is_finished, winner, score_str, s1, s2, _ = _resolve_match(t1, t2, live_scores)

        sf[slot_id] = {
            "team1": t1,
            "team2": t2,
            "score1": s1,
            "score2": s2,
            "winner": winner,
            "is_finished": is_finished,
            "is_live": False,
            "score_str": score_str,
            "label1": _pretty_feed_label(feed_a),
            "label2": _pretty_feed_label(feed_b)
        }
        
    # Final
    fa, fb = sf["SF_1"], sf["SF_2"]
    t1 = fa["winner"] if fa["is_finished"] else None
    t2 = fb["winner"] if fb["is_finished"] else None

    is_finished, winner, score_str, s1, s2, _ = (False, None, None, None, None, False)
    if t1 and t2:
        is_finished, winner, score_str, s1, s2, _ = _resolve_match(t1, t2, live_scores)

    final = {
        "team1": t1,
        "team2": t2,
        "score1": s1,
        "score2": s2,
        "winner": winner,
        "is_finished": is_finished,
        "is_live": False,
        "score_str": score_str,
        "label1": _pretty_feed_label("SF1"),
        "label2": _pretty_feed_label("SF2")
    }
    
    return {
        "r32": r32,
        "r16": r16,
        "qf": qf,
        "sf": sf,
        "final": {"FINAL": final},
        "champion": winner if is_finished else None
    }

def render_bracket_tree(live_scores):
    # Fetch data
    bracket_data = get_bracket_data(live_scores)
    
    # CSS Styles for Grid and Connectors
    st.markdown("""
<style>
.bracket-wrapper {
  overflow-x: auto;
  padding: 28px 16px;
  background: #030c03;
  border-radius: 16px;
  border: 1px solid rgba(74, 222, 128, 0.12);
  margin-bottom: 30px;
}
.bracket-grid {
  display: grid;
  grid-template-columns: 112px 14px 112px 14px 112px 14px 112px 14px 132px 14px 112px 14px 112px 14px 112px 14px 112px;
  grid-template-rows: repeat(15, 66px);
  gap: 0;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 1140px;
  margin: 0 auto;
}
.bracket-box {
  background: rgba(8, 28, 8, 0.85);
  border: 1px solid rgba(74, 222, 128, 0.18);
  border-radius: 8px;
  padding: 7px 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 56px;
  font-size: 0.92rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.15);
  transition: all 0.2s ease-in-out;
  box-sizing: border-box;
}
.bracket-box:hover {
  border-color: rgba(74, 222, 128, 0.4);
  transform: scale(1.03);
  z-index: 5;
}
.bracket-box.live {
  border-color: rgba(239, 68, 68, 0.5);
  background: rgba(40, 5, 5, 0.85);
  box-shadow: 0 0 12px rgba(239,68,68,0.2);
}
.bracket-box.empty {
  background: rgba(5, 15, 5, 0.5);
  border: 1px dashed rgba(74, 222, 128, 0.1);
}
.team-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  line-height: 1.35;
  font-weight: 600;
}
.team-row.placeholder {
  color: rgba(134, 239, 172, 0.65);
  font-style: italic;
  font-size: 0.74rem;
  font-weight: 500;
  letter-spacing: 0.01em;
}
.team-row.placeholder::before {
  content: "›";
  margin-right: 5px;
  color: rgba(251, 191, 36, 0.6);
  font-style: normal;
  font-weight: 800;
}
.team-row.winner {
  font-weight: 800;
  color: #f0fdf4;
}
.team-row.loser {
  color: rgba(134, 239, 172, 0.45);
  font-weight: 500;
}
.bracket-date {
  font-size: 0.68rem;
  color: rgba(134, 239, 172, 0.65);
  text-align: center;
  margin-top: 2px;
  font-weight: 500;
}
.pulsing-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  background-color: #ef4444;
  border-radius: 50%;
  margin-left: 4px;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { transform: scale(0.9); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.5; }
  100% { transform: scale(0.9); opacity: 1; }
}

/* SF / FINAL — grand, elevated styling distinct from regular rounds */
.bracket-box.grand-box {
  height: 64px;
  background: linear-gradient(145deg, rgba(40, 30, 6, 0.9), rgba(20, 16, 4, 0.95));
  border: 1.5px solid rgba(251, 191, 36, 0.4);
  box-shadow: 0 0 18px rgba(251, 191, 36, 0.12), 0 4px 10px rgba(0,0,0,0.3);
}
.bracket-box.grand-box:hover {
  border-color: rgba(251, 191, 36, 0.65);
  box-shadow: 0 0 24px rgba(251, 191, 36, 0.22), 0 4px 10px rgba(0,0,0,0.3);
}
.bracket-box.grand-box .team-row {
  font-size: 0.98rem;
}
.bracket-box.grand-box .team-row.winner {
  color: #fde68a;
}
.bracket-box.grand-box .team-row.placeholder {
  color: rgba(251, 191, 36, 0.55);
}
.bracket-box.grand-box .team-row.placeholder::before {
  color: rgba(251, 191, 36, 0.7);
}

.bracket-box.champion-box {
  height: 64px;
  background: linear-gradient(145deg, rgba(60, 44, 6, 0.95), rgba(251, 191, 36, 0.08));
  border: 2px solid rgba(251, 191, 36, 0.55);
  box-shadow: 0 0 26px rgba(251, 191, 36, 0.25), 0 4px 12px rgba(0,0,0,0.35);
}
.bracket-box.champion-box .team-row {
  color: #fde68a;
  font-weight: 800;
  font-size: 1.02rem;
  justify-content: center;
}

/* Connectors */
.line-cell {
  position: relative;
  width: 100%;
  height: 100%;
}
.line-left-top {
  position: absolute;
  top: 50%;
  left: 0;
  width: 50%;
  height: 50%;
  border-top: 2px solid rgba(74,222,128,0.3);
  border-right: 2px solid rgba(74,222,128,0.3);
}
.line-left-bottom {
  position: absolute;
  bottom: 50%;
  left: 0;
  width: 50%;
  height: 50%;
  border-bottom: 2px solid rgba(74,222,128,0.3);
  border-right: 2px solid rgba(74,222,128,0.3);
}
.line-left-mid {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 50%;
  height: 0;
  border-top: 2px solid rgba(74,222,128,0.3);
}
.line-left-vert {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 0;
  border-left: 2px solid rgba(74,222,128,0.3);
}
.line-right-top {
  position: absolute;
  top: 50%;
  right: 0;
  width: 50%;
  height: 50%;
  border-top: 2px solid rgba(74,222,128,0.3);
  border-left: 2px solid rgba(74,222,128,0.3);
}
.line-right-bottom {
  position: absolute;
  bottom: 50%;
  right: 0;
  width: 50%;
  height: 50%;
  border-bottom: 2px solid rgba(74,222,128,0.3);
  border-left: 2px solid rgba(74,222,128,0.3);
}
.line-right-mid {
  position: absolute;
  top: 50%;
  right: 50%;
  width: 50%;
  height: 0;
  border-top: 2px solid rgba(74,222,128,0.3);
}
.line-right-vert {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 50%;
  width: 0;
  border-right: 2px solid rgba(74,222,128,0.3);
}
.line-champion-vert {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 0;
  border-left: 2px solid rgba(251,191,36,0.4);
}

/* Match Cards */
.ko-card.right-glow {
  border-color: rgba(74, 222, 128, 0.45) !important;
  background: rgba(8, 36, 8, 0.95) !important;
  box-shadow: 0 0 16px rgba(74, 222, 128, 0.15);
}
.ko-card.wrong-glow {
  border-color: rgba(239, 68, 68, 0.4) !important;
  background: rgba(24, 8, 8, 0.95) !important;
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.1);
}
</style>
""", unsafe_allow_html=True)
    
    # Define grid cells
    grid_cells = {}
    
    # Left Side Matches
    grid_cells[(1, 1)] = ("match", "r32", "M3")
    grid_cells[(1, 3)] = ("match", "r32", "M6")
    grid_cells[(1, 5)] = ("match", "r32", "M1")
    grid_cells[(1, 7)] = ("match", "r32", "M4")
    grid_cells[(1, 9)] = ("match", "r32", "M13")
    grid_cells[(1, 11)] = ("match", "r32", "M11")
    grid_cells[(1, 13)] = ("match", "r32", "M10")
    grid_cells[(1, 15)] = ("match", "r32", "M9")
    
    grid_cells[(3, 2)] = ("match", "r16", "R16_1")
    grid_cells[(3, 6)] = ("match", "r16", "R16_2")
    grid_cells[(3, 10)] = ("match", "r16", "R16_3")
    grid_cells[(3, 14)] = ("match", "r16", "R16_4")
    
    grid_cells[(5, 4)] = ("match", "qf", "QF_1")
    grid_cells[(5, 12)] = ("match", "qf", "QF_2")
    
    grid_cells[(7, 8)] = ("match", "sf", "SF_1")
    
    # Center Matches
    grid_cells[(9, 8)] = ("match", "final", "FINAL")
    grid_cells[(9, 6)] = ("champion", None, None)
    
    # Right Side Matches
    grid_cells[(11, 8)] = ("match", "sf", "SF_2")
    
    grid_cells[(13, 4)] = ("match", "qf", "QF_3")
    grid_cells[(13, 12)] = ("match", "qf", "QF_4")
    
    grid_cells[(15, 2)] = ("match", "r16", "R16_5")
    grid_cells[(15, 6)] = ("match", "r16", "R16_6")
    grid_cells[(15, 10)] = ("match", "r16", "R16_7")
    grid_cells[(15, 14)] = ("match", "r16", "R16_8")
    
    grid_cells[(17, 1)] = ("match", "r32", "M2")
    grid_cells[(17, 3)] = ("match", "r32", "M5")
    grid_cells[(17, 5)] = ("match", "r32", "M7")
    grid_cells[(17, 7)] = ("match", "r32", "M8")
    grid_cells[(17, 9)] = ("match", "r32", "M15")
    grid_cells[(17, 11)] = ("match", "r32", "M14")
    grid_cells[(17, 13)] = ("match", "r32", "M12")
    grid_cells[(17, 15)] = ("match", "r32", "M16")
    
    # Left Connectors
    # Col 2
    grid_cells[(2, 1)] = ("line-left-top", None, None)
    grid_cells[(2, 2)] = ("line-left-join", None, None)
    grid_cells[(2, 3)] = ("line-left-bottom", None, None)
    grid_cells[(2, 5)] = ("line-left-top", None, None)
    grid_cells[(2, 6)] = ("line-left-join", None, None)
    grid_cells[(2, 7)] = ("line-left-bottom", None, None)
    grid_cells[(2, 9)] = ("line-left-top", None, None)
    grid_cells[(2, 10)] = ("line-left-join", None, None)
    grid_cells[(2, 11)] = ("line-left-bottom", None, None)
    grid_cells[(2, 13)] = ("line-left-top", None, None)
    grid_cells[(2, 14)] = ("line-left-join", None, None)
    grid_cells[(2, 15)] = ("line-left-bottom", None, None)
    
    # Col 4
    grid_cells[(4, 2)] = ("line-left-top", None, None)
    grid_cells[(4, 3)] = ("line-left-vert", None, None)
    grid_cells[(4, 4)] = ("line-left-join", None, None)
    grid_cells[(4, 5)] = ("line-left-vert", None, None)
    grid_cells[(4, 6)] = ("line-left-bottom", None, None)
    grid_cells[(4, 10)] = ("line-left-top", None, None)
    grid_cells[(4, 11)] = ("line-left-vert", None, None)
    grid_cells[(4, 12)] = ("line-left-join", None, None)
    grid_cells[(4, 13)] = ("line-left-vert", None, None)
    grid_cells[(4, 14)] = ("line-left-bottom", None, None)
    
    # Col 6
    grid_cells[(6, 4)] = ("line-left-top", None, None)
    for r in [5, 6, 7]: grid_cells[(6, r)] = ("line-left-vert", None, None)
    grid_cells[(6, 8)] = ("line-left-join", None, None)
    for r in [9, 10, 11]: grid_cells[(6, r)] = ("line-left-vert", None, None)
    grid_cells[(6, 12)] = ("line-left-bottom", None, None)
    
    # Col 8
    grid_cells[(8, 8)] = ("line-left-mid", None, None)
    
    # Col 9 vertical line between Final and Champion
    grid_cells[(9, 7)] = ("line-champion-vert", None, None)
    
    # Col 10
    grid_cells[(10, 8)] = ("line-right-mid", None, None)
    
    # Right Connectors
    # Col 12
    grid_cells[(12, 4)] = ("line-right-top", None, None)
    for r in [5, 6, 7]: grid_cells[(12, r)] = ("line-right-vert", None, None)
    grid_cells[(12, 8)] = ("line-right-join", None, None)
    for r in [9, 10, 11]: grid_cells[(12, r)] = ("line-right-vert", None, None)
    grid_cells[(12, 12)] = ("line-right-bottom", None, None)
    
    # Col 14
    grid_cells[(14, 2)] = ("line-right-top", None, None)
    grid_cells[(14, 3)] = ("line-right-vert", None, None)
    grid_cells[(14, 4)] = ("line-right-join", None, None)
    grid_cells[(14, 5)] = ("line-right-vert", None, None)
    grid_cells[(14, 6)] = ("line-right-bottom", None, None)
    grid_cells[(14, 10)] = ("line-right-top", None, None)
    grid_cells[(14, 11)] = ("line-right-vert", None, None)
    grid_cells[(14, 12)] = ("line-right-join", None, None)
    grid_cells[(14, 13)] = ("line-right-vert", None, None)
    grid_cells[(14, 14)] = ("line-right-bottom", None, None)
    
    # Col 16
    grid_cells[(16, 1)] = ("line-right-top", None, None)
    grid_cells[(16, 2)] = ("line-right-join", None, None)
    grid_cells[(16, 3)] = ("line-right-bottom", None, None)
    grid_cells[(16, 5)] = ("line-right-top", None, None)
    grid_cells[(16, 6)] = ("line-right-join", None, None)
    grid_cells[(16, 7)] = ("line-right-bottom", None, None)
    grid_cells[(16, 9)] = ("line-right-top", None, None)
    grid_cells[(16, 10)] = ("line-right-join", None, None)
    grid_cells[(16, 11)] = ("line-right-bottom", None, None)
    grid_cells[(16, 13)] = ("line-right-top", None, None)
    grid_cells[(16, 14)] = ("line-right-join", None, None)
    grid_cells[(16, 15)] = ("line-right-bottom", None, None)
    
    # Build HTML
    html = []
    html.append('<div class="bracket-wrapper">')
    html.append('<div class="bracket-grid">')
    
    for (col, row), cell_info in grid_cells.items():
        cell_type, round_name, slot_id = cell_info
        
        if cell_type == "match":
            match_data = bracket_data[round_name][slot_id]
            t1, t2 = match_data["team1"], match_data["team2"]
            s1, s2 = match_data["score1"], match_data["score2"]
            winner = match_data["winner"]
            is_finished = match_data["is_finished"]
            is_live = match_data["is_live"]
            
            box_class = "bracket-box"
            if round_name in ("sf", "final"):
                box_class += " grand-box"
            if is_live:
                box_class += " live"
            
            if t1 is None or t2 is None:
                box_class += " empty"

            if t1 is None and t2 is None:
                t1_html = f'<div class="team-row placeholder">{match_data.get("label1", "TBD")}</div>'
                t2_html = f'<div class="team-row placeholder">{match_data.get("label2", "TBD")}</div>'
                date_html = ""
            else:
                flag1 = FLAGS.get(NATION_TO_CODE.get(t1, ""), "⚽") if t1 else ""
                flag2 = FLAGS.get(NATION_TO_CODE.get(t2, ""), "⚽") if t2 else ""

                t1_cls = "team-row"
                t2_cls = "team-row"
                s1_h = ""
                s2_h = ""

                if is_finished:
                    if winner == t1:
                        t1_cls += " winner"
                        t2_cls += " loser"
                    elif winner == t2:
                        t1_cls += " loser"
                        t2_cls += " winner"
                    s1_h = f"<b>{s1}</b>"
                    s2_h = f"<b>{s2}</b>"
                elif is_live:
                    s1_h = f"<b>{s1 if s1 is not None else 0}</b>"
                    s2_h = f"<b>{s2 if s2 is not None else 0}</b>"

                if t1 is not None:
                    c1 = TEAM_COLORS.get(NATION_TO_CODE.get(t1, ""), "rgba(74,222,128,0.3)")
                    t1_disp = f'{flag1} <span style="display: inline-block; max-width: 74px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; vertical-align: middle;">{t1}</span>'
                    t1_html = f'<div class="{t1_cls}" style="border-left: 3px solid {c1}; padding-left: 6px; border-radius: 2px;">{t1_disp} {s1_h}</div>'
                else:
                    t1_html = f'<div class="team-row placeholder">{match_data.get("label1", "TBD")}</div>'

                if t2 is not None:
                    c2 = TEAM_COLORS.get(NATION_TO_CODE.get(t2, ""), "rgba(74,222,128,0.3)")
                    t2_disp = f'{flag2} <span style="display: inline-block; max-width: 74px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; vertical-align: middle;">{t2}</span>'
                    t2_html = f'<div class="{t2_cls}" style="border-left: 3px solid {c2}; padding-left: 6px; border-radius: 2px;">{t2_disp} {s2_h}</div>'
                else:
                    t2_html = f'<div class="team-row placeholder">{match_data.get("label2", "TBD")}</div>'

                date_val = match_data.get("date", "")
                if round_name == "r32" and date_val:
                    date_html = f'<div class="bracket-date">{date_val}</div>'
                else:
                    date_html = ""
            
            live_dot = ' <span class="pulsing-dot"></span>' if is_live else ""
            if round_name == "r32":
                _slot_display = slot_id
            elif round_name == "r16":
                _slot_display = f"R16 · {slot_id.split('_')[1]}"
            elif round_name == "qf":
                _slot_display = f"QF {slot_id.split('_')[1]}"
            elif round_name == "sf":
                _slot_display = f"SF {slot_id.split('_')[1]}"
            elif round_name == "final":
                _slot_display = "FINAL"
            else:
                _slot_display = slot_id
            slot_label = f'<div style="font-size:0.5rem;color:rgba(74,222,128,0.4);font-weight:700;margin-bottom:2px;display:flex;justify-content:space-between;align-items:center;letter-spacing:0.04em;text-transform:uppercase;"><span>{_slot_display}</span>{live_dot}</div>'
            
            html.append(f'<div class="{box_class}" style="grid-column: {col}; grid-row: {row};">')
            html.append(slot_label)
            html.append(t1_html)
            html.append(t2_html)
            html.append(date_html)
            html.append('</div>')
            
        elif cell_type == "champion":
            champ = bracket_data["champion"]
            if champ:
                flag = FLAGS.get(NATION_TO_CODE.get(champ, ""), "⚽")
                html.append(f'''<div class="bracket-box champion-box" style="grid-column: {col}; grid-row: {row};">
                    <div style="font-size:0.55rem;color:#fbbf24;text-transform:uppercase;letter-spacing:0.1em;text-align:center;font-weight:700;margin-bottom:2px;">🏆 CHAMPION 🏆</div>
                    <div class="team-row" style="color:#fbbf24;font-weight:800;font-size:0.85rem;justify-content:center;">
                        {flag} &nbsp; {champ}
                    </div>
                </div>''')
            else:
                html.append(f'''<div class="bracket-box champion-box empty" style="grid-column: {col}; grid-row: {row}; border: 1px dashed rgba(251, 191, 36, 0.2); background: rgba(251,191,36,0.02);">
                    <div style="font-size:0.55rem;color:rgba(251,191,36,0.5);text-transform:uppercase;letter-spacing:0.1em;text-align:center;font-weight:700;margin-bottom:2px;">🏆 CHAMPION 🏆</div>
                    <div class="team-row placeholder" style="color:rgba(251,191,36,0.4);font-size:0.75rem;justify-content:center;font-style:italic;">
                        TBD
                    </div>
                </div>''')
                
        elif cell_type.startswith("line-"):
            inner_class = cell_type
            html.append(f'<div style="grid-column: {col}; grid-row: {row}; width:100%; height:100%;">')
            html.append('<div class="line-cell">')
            
            if cell_type == "line-left-join":
                html.append('<div class="line-left-vert"></div><div class="line-left-mid"></div>')
            elif cell_type == "line-right-join":
                html.append('<div class="line-right-vert"></div><div class="line-right-mid"></div>')
            else:
                html.append(f'<div class="{inner_class}"></div>')
                
            html.append('</div>')
            html.append('</div>')
            
    html.append('</div>')
    html.append('</div>')
    
    st.markdown("".join(html), unsafe_allow_html=True)

def _render_knockout_card(col, t1, t2, slot_label, round_title, meta_html, live_scores):
    """Renders one prediction/result card for a single real matchup
    (used for R32, and for R16/QF/SF/Final once both teams are confirmed)."""
    f1 = FLAGS.get(NATION_TO_CODE.get(t1, ""), "⚽")
    f2 = FLAGS.get(NATION_TO_CODE.get(t2, ""), "⚽")

    pred_w, adj1, adj2 = knockout_predict(t1, t2)
    wpct = adj1 if pred_w == t1 else adj2

    is_finished, act_winner, score_str, s1, s2, _ = _resolve_match(t1, t2, live_scores)

    if is_finished:
        is_correct = (act_winner == pred_w)
        glow_class = "right-glow" if is_correct else "wrong-glow"
        badge_html = f'<div class="ko-badge actual">{"✅ Right Prediction" if is_correct else "❌ Wrong Prediction"}</div>'

        score_main = score_str
        details = ""
        if " " in score_str:
            score_main, details = score_str.split(" ", 1)
        score_parts = score_main.split("\u2013")
        s1_part = score_parts[0]
        s2_part = score_parts[1] if len(score_parts) > 1 else ""
        details_html = f'<div style="font-size:0.9rem;color:#86efac;margin-top:2px;">{details}</div>' if details else ""

        score_html = (
            f'<div class="ko-score" style="margin-bottom:8px;">{f1} {s1_part} '
            f'<span style="color:#4b7c4b;">\u2013</span> '
            f'{s2_part} {f2}</div>'
            f'{details_html}'
        )
    else:
        act_winner = None
        glow_class = ""
        badge_html = f'<div class="ko-badge">Predicted: {f1 if pred_w==t1 else f2} {pred_w} {wpct}%</div>'
        score_html = ""

    t1_bold = "font-weight:800;color:#4ade80;" if is_finished and act_winner == t1 else ""
    t2_bold = "font-weight:800;color:#4ade80;" if is_finished and act_winner == t2 else ""
    c1 = TEAM_COLORS.get(NATION_TO_CODE.get(t1, ""), "rgba(74,222,128,0.3)")
    c2 = TEAM_COLORS.get(NATION_TO_CODE.get(t2, ""), "rgba(74,222,128,0.3)")

    card_html = clean_html(f'''
    <div class="ko-card {glow_class}">
        <div class="ko-slot">{slot_label} \u00b7 {round_title}</div>
        <div class="ko-teams">
            <span style="{t1_bold} border-left:3px solid {c1}; padding-left:6px; border-radius:2px;">{f1} {t1}</span>
            <span style="color:#4b7c4b;font-size:0.85rem;padding:0 8px;">vs</span>
            <span style="{t2_bold} border-left:3px solid {c2}; padding-left:6px; border-radius:2px;">{f2} {t2}</span>
        </div>
        {meta_html}
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
            <div class="star-box" style="padding:10px 14px;">
                <div style="font-size:0.75rem;color:#86efac;margin-bottom:4px;">{f1} {t1}</div>
                <div style="font-size:1.4rem;font-weight:800;color:#4ade80;">{adj1}%</div>
                <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{adj1}%;background:linear-gradient(90deg,#4ade80,#22c55e);"></div></div>
            </div>
            <div class="star-box" style="padding:10px 14px;">
                <div style="font-size:0.75rem;color:#86efac;margin-bottom:4px;">{f2} {t2}</div>
                <div style="font-size:1.4rem;font-weight:800;color:#4ade80;">{adj2}%</div>
                <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{adj2}%;background:linear-gradient(90deg,#4ade80,#22c55e);"></div></div>
            </div>
        </div>
        {score_html}
        {badge_html}
    </div>''')

    with col:
        st.markdown(card_html, unsafe_allow_html=True)

def render_match_cards(live_scores, bracket_data):
    st.markdown("### \u2694\ufe0f Round of 32 \u2014 All 16 Matches")
    st.markdown('<p class="page-sub" style="margin-top:-12px;margin-bottom:16px;">Detailed model predictions and actual knockout results</p>', unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, match in enumerate(WC_ROUND_OF_32):
        meta_html = f'<div class="ko-meta">\U0001F4C5 {match["date"]} \u00b7 \U0001F3DF\ufe0f {match["venue"]} \u00b7 \U0001F4CD {match["city"]}</div>'
        _render_knockout_card(cols[idx % 2], match["team1"], match["team2"], match["slot"], "Round of 32", meta_html, live_scores)

    # Show prediction cards for later rounds ONLY once both teams in that
    # matchup are actually confirmed -- never speculating multiple rounds
    # ahead, just keeping pace with rounds as they become real.
    round_defs = [
        ("r16", "Round of 16", ["R16_1","R16_2","R16_3","R16_4","R16_5","R16_6","R16_7","R16_8"]),
        ("qf", "Quarterfinals", ["QF_1","QF_2","QF_3","QF_4"]),
        ("sf", "Semifinals", ["SF_1","SF_2"]),
        ("final", "Final", ["FINAL"]),
    ]
    for round_key, round_title, slot_ids in round_defs:
        live_slots = [sid for sid in slot_ids if bracket_data[round_key][sid]["team1"] and bracket_data[round_key][sid]["team2"]]
        if not live_slots:
            continue
        st.markdown("---")
        st.markdown(f"### \u2694\ufe0f {round_title} \u2014 {len(live_slots)} Match{'es' if len(live_slots)!=1 else ''} Confirmed")
        st.markdown('<p class="page-sub" style="margin-top:-12px;margin-bottom:16px;">Updates automatically as earlier rounds are decided</p>', unsafe_allow_html=True)
        rcols = st.columns(2)
        for i, slot_id in enumerate(live_slots):
            m = bracket_data[round_key][slot_id]
            slot_display = "FINAL" if round_key == "final" else f"{round_title.split()[0]} {slot_id.split('_')[1]}" if "_" in slot_id else slot_id
            _render_knockout_card(rcols[i % 2], m["team1"], m["team2"], slot_display, round_title, "", live_scores)



def get_squad(team):
    code = NATION_TO_CODE.get(team,"")
    if not code: return pd.DataFrame()
    return df[df["Nation"]==code].sort_values("Overall_Index",ascending=False)

# ── HORIZONTAL TAB NAVIGATION ─────────────────────────────────────────────
tab_mi, tab_sched, tab_nat, tab_bracket = st.tabs([
    "🔥 Match Intelligence",
    "📅 Schedule",
    "🌍 Nations & Players",
    "🏆 Knockout Bracket",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — MATCH INTELLIGENCE (main tab)
# ════════════════════════════════════════════════════════════════════════════
with tab_mi:
    st.markdown('<p class="page-title">🔥 Match Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Every match. Every star. Every storyline. Your pregame scouting report.</p>', unsafe_allow_html=True)


    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel_group = st.selectbox("📂 Group", [f"Group {g}" for g in GROUPS.keys()])
    gkey = sel_group.split(" ")[1]
    grp_matches = [m for m in WC_SCHEDULE if m["group"]==gkey]
    match_labels = [f"{m['team1']}  vs  {m['team2']}  —  {m['date']}" for m in grp_matches]
    with col_sel2:
        sel_match = st.selectbox("⚽ Match", match_labels)

    mi = grp_matches[match_labels.index(sel_match)]
    team1, team2 = mi["team1"], mi["team2"]
    c1 = NATION_TO_CODE.get(team1,""); c2 = NATION_TO_CODE.get(team2,"")
    f1 = FLAGS.get(c1,"🏳️"); f2 = FLAGS.get(c2,"🏳️")

    # Match header
    st.markdown(clean_html(f"""
    <div class="match-hdr">
        <div style="display:flex;justify-content:center;align-items:center;gap:20px;flex-wrap:wrap;">
            <div><div style="font-size:3rem;">{f1}</div><div class="match-team">{team1}</div></div>
            <div class="match-vs">VS</div>
            <div><div style="font-size:3rem;">{f2}</div><div class="match-team">{team2}</div></div>
        </div>
        <div style="margin-top:18px;">
            <span class="mpill">🏆 Group {gkey} · FIFA World Cup 2026</span>
            <span class="mpill">📅 {mi['date']} · {mi['time']}</span>
            <span class="mpill">🏟️ {mi['venue']}</span>
            <span class="mpill">📍 {mi['city']}</span>
        </div>
    </div>"""), unsafe_allow_html=True)

    # Get squads
    t1p = get_squad(team1); t2p = get_squad(team2)
    top5_t1 = t1p.head(5); top5_t2 = t2p.head(5)

    # Win probability
    wp1, wpd, wp2 = win_probability(team1, team2)
    is_underdog = team2 if wp1 > wp2+20 else (team1 if wp2 > wp1+20 else None)
    fav = team1 if wp1 >= wp2 else team2

    # Win prob display
    st.markdown("### 🎲 Win Probability")
    pc1, pcd, pc2 = st.columns(3)
    with pc1:
        st.markdown(clean_html(f"""
        <div class="star-box" style="border-color:rgba(74,222,128,0.25);">
            <div style="font-size:0.8rem;color:#86efac;margin-bottom:6px;">{f1} {team1}</div>
            <div style="font-size:2.5rem;font-weight:800;color:#4ade80;">{wp1}%</div>
            <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{wp1}%;background:linear-gradient(90deg,#4ade80,#22c55e);"></div></div>
        </div>"""), unsafe_allow_html=True)
    with pcd:
        st.markdown(clean_html(f"""
        <div class="star-box">
            <div style="font-size:0.8rem;color:#86efac;margin-bottom:6px;">Draw</div>
            <div style="font-size:2.5rem;font-weight:800;color:#fbbf24;">{wpd}%</div>
            <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{wpd}%;background:#fbbf24;"></div></div>
        </div>"""), unsafe_allow_html=True)
    with pc2:
        st.markdown(clean_html(f"""
        <div class="star-box" style="border-color:rgba(74,222,128,0.25);">
            <div style="font-size:0.8rem;color:#86efac;margin-bottom:6px;">{f2} {team2}</div>
            <div style="font-size:2.5rem;font-weight:800;color:#4ade80;">{wp2}%</div>
            <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{wp2}%;background:linear-gradient(90deg,#4ade80,#22c55e);"></div></div>
        </div>"""), unsafe_allow_html=True)

    # Underdog story
    if is_underdog:
        uf = FLAGS.get(NATION_TO_CODE.get(is_underdog,""),"⚽")
        fav_f = FLAGS.get(NATION_TO_CODE.get(fav,""),"⚽")
        st.markdown(clean_html(f"""
        <div class="gem-box">
            <div style="font-size:1rem;font-weight:700;color:#fbbf24;margin-bottom:8px;">🐴 David vs Goliath Alert</div>
            <div style="color:#fde68a;font-size:0.95rem;line-height:1.7;">
                {uf} <strong>{is_underdog}</strong> walks into this one as the underdog — but in World Cup history, 
                that tag has meant nothing. Remember Saudi Arabia beating Argentina in 2022? Morocco reaching the semis?
                The beautiful game doesn't care about the odds. <strong>{is_underdog}</strong> is the dark horse of this group. Don't count them out. 🌍
            </div>
        </div>"""), unsafe_allow_html=True)

    # Players to watch
    st.markdown("### 👀 Players to Watch")
    pw1, pw2 = st.columns(2)

    def player_panel(players, team, flag):
        h = f'<div style="background:rgba(8,28,8,0.8);border:1px solid rgba(74,222,128,0.1);border-radius:14px;padding:18px;">'
        h += f'<div style="font-size:1rem;font-weight:700;color:#f0fdf4;margin-bottom:14px;">{flag} {team}</div>'
        if players.empty:
            h += '<div style="color:#86efac;font-size:0.88rem;padding:8px;">No Big 5 league data available for this nation.</div>'
        else:
            for rank,(_,r) in enumerate(players.iterrows(),1):
                sc=r["Overall_Index"]; col=score_color(sc)
                h += f'''<div class="mini-row">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="color:#4b7c4b;font-weight:700;font-size:0.82rem;">#{rank}</span>
                        <div>
                            <div style="color:#f0fdf4;font-weight:600;font-size:0.92rem;">{r["Player"]}</div>
                            <div style="color:#4b7c4b;font-size:0.76rem;">{r["Squad"]} · {r["Archetype_V2"]}</div>
                        </div>
                    </div>
                    <div style="color:{col};font-weight:800;font-size:1.05rem;">{sc:.1f}</div>
                </div>'''
        h += '</div>'
        return h

    with pw1: st.markdown(clean_html(player_panel(top5_t1,team1,f1)), unsafe_allow_html=True)
    with pw2: st.markdown(clean_html(player_panel(top5_t2,team2,f2)), unsafe_allow_html=True)

    # Intensity + star power side by side
    st.markdown("### ⚡ Match Intensity  &  ⭐ Star Power")
    ic1, ic2 = st.columns([3,2])

    s1 = top5_t1["Overall_Index"].tolist() if not top5_t1.empty else [10]
    s2 = top5_t2["Overall_Index"].tolist() if not top5_t2.empty else [10]
    intensity_score = round((np.mean(s1)+np.mean(s2))/2,1)
    ilabel,icolor,ibg = get_intensity(intensity_score)

    with ic1:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=intensity_score,
            title={"text":"Match Intensity","font":{"size":16,"color":"#86efac","family":"Plus Jakarta Sans"}},
            number={"font":{"size":44,"color":"#f0fdf4","family":"Plus Jakarta Sans"},"suffix":""},
            gauge={"axis":{"range":[0,100],"tickcolor":"rgba(74,222,128,0.3)","tickfont":{"color":"#86efac","size":9}},
                   "bar":{"color":icolor,"thickness":0.25},"bgcolor":"rgba(8,28,8,0.5)","borderwidth":0,
                   "steps":[{"range":[0,50],"color":"rgba(34,197,94,0.05)"},{"range":[50,70],"color":"rgba(234,179,8,0.05)"},
                             {"range":[70,85],"color":"rgba(249,115,22,0.07)"},{"range":[85,100],"color":"rgba(239,68,68,0.08)"}],
                   "threshold":{"line":{"color":icolor,"width":3},"thickness":0.8,"value":intensity_score}}))
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#f0fdf4',family='Plus Jakarta Sans'),
                            height=240,margin=dict(l=20,r=20,t=40,b=10))
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(clean_html(f'<div style="text-align:center;margin-top:-10px;"><span style="background:{ibg};color:{icolor};border:1px solid {icolor}40;padding:8px 22px;border-radius:9999px;font-size:1rem;font-weight:800;">{ilabel}</span></div>'), unsafe_allow_html=True)
    if intensity_score >= 85:
        confetti()

    with ic2:
        wc1 = len(t1p[t1p["WC_Watchlist_V2"]]) if not t1p.empty else 0
        wc2 = len(t2p[t2p["WC_Watchlist_V2"]]) if not t2p.empty else 0
        stronger = 1 if wc1 >= wc2 else 2
        for i,(wc,team,flag) in enumerate([(wc1,team1,f1),(wc2,team2,f2)],1):
            border = "border-color:#fbbf24;box-shadow:0 0 16px rgba(251,191,36,0.15);" if stronger==i else ""
            crown = '<div style="color:#fbbf24;font-size:0.75rem;font-weight:700;margin-top:4px;">👑 STRONGER SQUAD</div>' if stronger==i else ''
            st.markdown(clean_html(f'<div class="star-box" style="{border}margin-bottom:10px;"><div style="font-size:0.85rem;color:#86efac;margin-bottom:4px;">{flag} {team}</div><div class="star-num">⭐ {wc}</div><div style="color:#4b7c4b;font-size:0.8rem;margin-top:4px;">WC Watchlist Players</div>{crown}</div>'), unsafe_allow_html=True)

    # Hidden gems
    g1 = t1p[t1p["Hidden_Gem"]] if not t1p.empty else pd.DataFrame()
    g2 = t2p[t2p["Hidden_Gem"]] if not t2p.empty else pd.DataFrame()
    all_gems = pd.concat([g1,g2]).sort_values("Overall_Index",ascending=False)
    if not all_gems.empty:
        rows=""
        for _,g in all_gems.iterrows():
            gteam = team1 if g["Nation"]==c1 else team2
            gf = FLAGS.get(g["Nation"],"⚽")
            rows += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(251,191,36,0.08);"><div><span style="color:#fcd34d;font-weight:700;">{gf} {g["Player"]}</span><span style="color:#86efac;font-size:0.82rem;margin-left:8px;">· {g["Squad"]} · {g["Archetype_V2"]}</span></div><span style="background:rgba(245,158,11,0.2);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);padding:2px 10px;border-radius:9999px;font-weight:700;font-size:0.82rem;">{g["Overall_Index"]:.1f}</span></div>'
        st.markdown(clean_html(f'<div class="gem-box"><div style="font-size:0.95rem;font-weight:700;color:#f59e0b;margin-bottom:10px;">👀 Hidden Gem Alert</div>{rows}</div>'), unsafe_allow_html=True)

    # Head to Head History
    h2h_key = frozenset([team1, team2])
    if h2h_key in H2H:
        st.markdown("### ⚔️ Head-to-Head History")
        h2h_records = H2H[h2h_key]
        h2h_html = ""
        for rec in h2h_records:
            winner_flag = f1 if rec["winner"]==team1 else (f2 if rec["winner"]==team2 else "🤝")
            win_color = "#4ade80" if rec["winner"]==team1 else ("#ef4444" if rec["winner"]==team2 else "#fbbf24")
            h2h_html += clean_html(f'''<div class="h2h-card">
                <div class="h2h-year">{rec["year"]} World Cup · {rec["round"]}</div>
                <div class="h2h-result">{winner_flag} {rec["winner"]} <span style="color:#4b7c4b;font-size:0.85rem;">won</span> {rec["score"]}</div>
                <div class="h2h-note">📖 {rec["note"]}</div>
            </div>''')
        st.markdown(h2h_html, unsafe_allow_html=True)
    else:
        st.markdown("### ⚔️ Head-to-Head History")
        st.markdown(clean_html(f'''<div class="h2h-card">
            <div class="h2h-year">No previous World Cup meetings</div>
            <div class="h2h-result" style="color:#86efac;">First time these nations meet at a World Cup 🆕</div>
            <div class="h2h-note">📖 History waits to be written. Which team writes the first chapter?</div>
        </div>'''), unsafe_allow_html=True)

    # The Storyline
    st.markdown("### 🎙️ The Storyline")
    def top_info(players):
        if players.empty: return "a key player","their club","a dangerous talent"
        t=players.iloc[0]; return t["Player"],t["Squad"],t["Archetype_V2"]

    p1n,p1c,p1a = top_info(top5_t1)
    p2n,p2c,p2a = top_info(top5_t2)

    if intensity_score >= 85:
        story = f"🏟️ {team1} vs {team2} — mark this one in RED on your calendar.\n\n{p1n} has been UNREAL this season at {p1c}. As a {p1a}, he controls games the way an NFL quarterback controls a drive — with precision, with flair, and with the weight of a nation on his shoulders. On the other side, {team2} brings {p2n} from {p2c}, and when this {p2a} gets the ball in dangerous areas? Defenders hold their breath.\n\nWith a Match Intensity Score of {intensity_score:.0f}, this is as elite as the World Cup gets. Two powerhouses. One pitch. Zero guarantees. This is what the beautiful game was made for. 🌍⚽🔥"
    elif intensity_score >= 70:
        story = f"📺 Set your alarm — {team1} vs {team2} has the ingredients of a genuine World Cup classic.\n\n{p1n} ({p1c}) brings the kind of {p1a} energy that turns group stage matches into highlight reels. And {team2}'s {p2n} is no pushover either — this is a tactical chess match wrapped in a football game, and at the World Cup, those tend to be the most entertaining ones.\n\nIntensity Score: {intensity_score:.0f}. High quality, high stakes. Don't miss it. ⚽"
    elif intensity_score >= 50:
        story = f"👀 Don't overlook {team1} vs {team2} — there's more here than meets the eye.\n\n{p1n} has been quietly putting together a strong season at {p1c} as a {p1a}, and in knockout-adjacent football, one moment of brilliance changes everything. {team2}'s {p2n} from {p2c} could be the wildcard nobody sees coming.\n\nIntensity Score: {intensity_score:.0f}. This could be the dark horse match of the group. 👀"
    else:
        story = f"⚽ Every World Cup has its 'sleeper' matches — and {team1} vs {team2} might just be that.\n\nBut here's the thing about the World Cup: upsets HAPPEN every single tournament. Remember Iceland? Cameroon? South Korea 2002? {p1n} ({p1c}) as a {p1a} is the kind of player who saves his best for the biggest stage, and this might be exactly when {team2} announces themselves to the world.\n\nIntensity Score: {intensity_score:.0f}. Sometimes the quietest matches produce the loudest moments. Don't tune out too early. 🌍"

    st.markdown(clean_html(f"""
    <div class="storyline">
        <div style="font-size:0.72rem;color:#4ade80;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;margin-bottom:14px;">🎙️ Match Preview · {mi['date']} · {mi['venue']} · {mi['city']}</div>
        <div style="white-space:pre-line;">{story}</div>
        <div style="margin-top:16px;padding-top:14px;border-top:1px solid rgba(74,222,128,0.08);display:flex;gap:10px;flex-wrap:wrap;">
            <span style="background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.2);color:#4ade80;padding:3px 12px;border-radius:9999px;font-size:0.76rem;font-weight:600;">Group {gkey}</span>
            <span style="background:{ibg};border:1px solid {icolor}40;color:{icolor};padding:3px 12px;border-radius:9999px;font-size:0.76rem;font-weight:600;">{ilabel}</span>
            <span style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.2);color:#fcd34d;padding:3px 12px;border-radius:9999px;font-size:0.76rem;font-weight:600;">{f1} {wp1}% · Draw {wpd}% · {f2} {wp2}%</span>
        </div>
    </div>"""), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — SCHEDULE
# ════════════════════════════════════════════════════════════════════════════
with tab_sched:
    st.markdown('<p class="page-title">📅 Full Group Stage Schedule</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">All 72 group stage matches · June 11 – June 25, 2026 · USA, Mexico & Canada</p>', unsafe_allow_html=True)
    # Load live scores
    live_scores = fetch_live_scores()
    # Countdown timer


    # Filter
    with st.expander("🔍 Filter by Group or Date", expanded=False):
        sc1, sc2 = st.columns(2)
        with sc1: sched_groups = st.multiselect("Groups", [f"Group {g}" for g in GROUPS.keys()], default=[f"Group {g}" for g in GROUPS.keys()], key="sg")
        with sc2: sched_search = st.text_input("Search team", placeholder="e.g. England, Brazil...", key="ss")

    sel_group_keys = [g.split(" ")[1] for g in sched_groups] if sched_groups else list(GROUPS.keys())
    filtered_schedule = [m for m in WC_SCHEDULE if m["group"] in sel_group_keys]
    if sched_search:
        filtered_schedule = [m for m in filtered_schedule if sched_search.lower() in m["team1"].lower() or sched_search.lower() in m["team2"].lower()]

    # Sort by date then show date-grouped
    date_order = ["Jun 11","Jun 12","Jun 13","Jun 14","Jun 15","Jun 16",
                  "Jun 17","Jun 18","Jun 19","Jun 20","Jun 21","Jun 22",
                  "Jun 23","Jun 24","Jun 25"]
    filtered_schedule.sort(key=lambda m: (date_order.index(m["date"]) if m["date"] in date_order else 99, m["group"]))
    seen_dates = []
    date_groups = {}
    for m in filtered_schedule:
        d = m["date"]
        if d not in date_groups:
            date_groups[d] = []
            seen_dates.append(d)
        date_groups[d].append(m)
    for date_key in seen_dates:
        day_list = date_groups[date_key]
        st.markdown(f"#### 📅 {date_key}")
        html = '<div class="sched-group">'
        for m in day_list:
            f_t1 = FLAGS.get(NATION_TO_CODE.get(m["team1"],""),"⚽")
            f_t2 = FLAGS.get(NATION_TO_CODE.get(m["team2"],""),"⚽")
            wp_1, wp_d, wp_2 = win_probability(m["team1"], m["team2"])
            time_str = m["time"] if m["time"]!="TBD" else "Time TBD"
            c1 = NATION_TO_CODE.get(m["team1"],""); c2 = NATION_TO_CODE.get(m["team2"],"")
            avg = round((team_avg(c1)+team_avg(c2))/2,1)
            ilabel,icolor,_ = get_intensity(avg)
            # Check live score
            s1, s2, g1, g2 = get_match_score(m["team1"], m["team2"], live_scores)
            if s1 is not None:
                # Match played — show real score + prediction accuracy
                winner = m["team1"] if s1>s2 else (m["team2"] if s2>s1 else "Draw")
                wcol = "#4ade80" if s1>s2 else ("#ef4444" if s2>s1 else "#fbbf24")
                pred_winner = m["team1"] if wp_1>wp_2 else (m["team2"] if wp_2>wp_1 else "Draw")
                pred_flag = f_t1 if wp_1>wp_2 else (f_t2 if wp_2>wp_1 else "🤝")
                correct = winner == pred_winner
                pcol = "#4ade80" if correct else "#ef4444"
                ptext = ("✅ Predicted " if correct else "❌ Predicted ") + f"{pred_flag} {pred_winner}"
                right_html = (
                    f'<div style="text-align:right;min-width:200px;">'
                    f'<div style="font-size:1.5rem;font-weight:900;color:#f0fdf4;">{s1} <span style="color:#4b7c4b;font-size:0.9rem;">—</span> {s2}</div>'
                    f'<div style="font-size:0.72rem;color:{wcol};font-weight:700;">{"🏆 "+winner+" wins" if winner!="Draw" else "🤝 Draw"}</div>'
                    f'<div style="font-size:0.68rem;color:{pcol};margin-top:3px;font-weight:600;">{ptext}</div>'
                    f'</div>'
                )
            else:
                # Not played yet — show prediction
                pred_winner = m["team1"] if wp_1>wp_2 else (m["team2"] if wp_2>wp_1 else "Draw")
                pred_flag = f_t1 if wp_1>wp_2 else (f_t2 if wp_2>wp_1 else "🤝")
                right_html = f'<div style="text-align:right;min-width:220px;"><div style="font-size:0.65rem;color:#4b7c4b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:2px;">Predicted</div><div style="font-size:0.82rem;font-weight:700;color:#fbbf24;margin-bottom:4px;">{pred_flag} {pred_winner}</div><div style="font-size:0.72rem;color:{icolor};font-weight:700;margin-bottom:3px;">{ilabel}</div><div style="font-size:0.72rem;color:#86efac;">{f_t1} {wp_1}% · {wp_d}% Draw · {wp_2}% {f_t2}</div><div class="prob-bar-wrap" style="width:140px;margin-left:auto;margin-top:4px;"><div class="prob-bar-fill" style="width:{wp_1}%;background:linear-gradient(90deg,#4ade80,#22c55e);"></div></div></div>'
            html += f'<div class="sched-match"><div style="flex:1;"><div class="sched-teams">{f_t1} {m["team1"]} <span style="color:#4b7c4b;font-size:0.8rem;padding:0 8px;">vs</span> {m["team2"]} {f_t2}</div><div class="sched-meta" style="margin-top:4px;"><span style="background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.15);color:#4ade80;padding:2px 8px;border-radius:9999px;font-size:0.72rem;font-weight:600;margin-right:6px;">Group {m["group"]}</span>🏟️ {m["venue"]} · 📍 {m["city"]} · ⏰ {time_str}</div></div>{right_html}</div>'
        html += '</div>'
        st.markdown(clean_html(html),unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — KNOCKOUT BRACKET
# ════════════════════════════════════════════════════════════════════════════
with tab_bracket:
    # Helper to find the next upcoming knockout match (Round of 32)
    def _next_ko_match(ko_live):
        """
        Return the next upcoming knockout match.
        - Skip if API has a score (finished)
        - Skip if kickoff was more than 2.5 hours ago (match window over)
        - Do NOT skip just because kickoff time has passed (match may be live)
        """
        now_utc = datetime.now(timezone.utc)
        for m in sorted(WC_ROUND_OF_32, key=_parse_ko_date_utc):
            s1, s2, _, _ = get_match_score(m["team1"], m["team2"], ko_live)
            if s1 is not None:
                continue  # confirmed finished by API
            kickoff = _parse_ko_date_utc(m)
            if kickoff and (now_utc - kickoff).total_seconds() > 9000:
                continue  # more than 2.5 hours since kickoff, assume done
            return m
        return None
    st.markdown('<p class="page-title">🏆 Knockout Bracket</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Follow the visual bracket tree and explore predicted matchups vs actual results.</p>', unsafe_allow_html=True)
    
    ko_live = fetch_live_scores()
    next_ko = _next_ko_match(ko_live)
    
    # Next Up hero countdown
    if next_ko:
        nk_t1, nk_t2 = next_ko["team1"], next_ko["team2"]
        nk_f1, nk_f2 = _ko_flag(nk_t1), _ko_flag(nk_t2)
        nk_pred, nk_adj1, nk_adj2 = knockout_predict(nk_t1, nk_t2)
        nk_wflag = nk_f1 if nk_pred == nk_t1 else nk_f2
        nk_wpct = nk_adj1 if nk_pred == nk_t1 else nk_adj2
        nk_ts = int(_parse_ko_date_utc(next_ko).timestamp() * 1000)
        nk_hero = (
            "<!DOCTYPE html><html><body style='margin:0;padding:0;background:#061a06;'>"
            "<div style='background:linear-gradient(135deg,rgba(8,28,8,0.97),rgba(3,10,3,0.99));"
            "border:1px solid rgba(74,222,128,0.2);border-radius:16px;padding:20px 32px;text-align:center;'>"
            "<div style='font-size:0.65rem;color:#4ade80;text-transform:uppercase;"
            "letter-spacing:0.22em;font-weight:700;margin-bottom:8px;'>Next Up · Round of 32</div>"
            f"<div style='font-size:1.5rem;font-weight:900;color:#f0fdf4;margin-bottom:4px;'>"
            f"{nk_f1} {nk_t1} <span style='color:#4b7c4b;font-size:1rem;padding:0 8px;'>vs</span> "
            f"{nk_t2} {nk_f2}</div>"
            f"<div style='font-size:0.72rem;color:#86efac;margin-bottom:8px;'>"
            f"{next_ko['slot']} · {next_ko['date']} · {next_ko['venue']} · {next_ko['city']}</div>"
            f"<div style='font-size:0.85rem;color:#fbbf24;font-weight:700;margin-bottom:10px;'>"
            f"Predicted: {nk_wflag} {nk_pred} {nk_wpct}%</div>"
            "<div id='ko-timer' style='font-size:2.2rem;font-weight:900;color:#fbbf24;"
            "font-variant-numeric:tabular-nums;'>--</div>"
            "</div>"
            f"<script>"
            f"(function(){{var t={nk_ts};var el=document.getElementById('ko-timer');"
            f"function tick(){{var d=t-Date.now();if(d<=0){{el.textContent='Kickoff!';return;}}"
            f"var days=Math.floor(d/86400000);var hrs=Math.floor((d%86400000)/3600000);"
            f"var mins=Math.floor((d%3600000)/60000);var secs=Math.floor((d%60000)/1000);"
            f"el.textContent=(days>0?days+'d ':'')+hrs+'h '+mins+'m '+secs+'s';}}"
            f"tick();setInterval(tick,1000);}})();"
            f"</script>"
            "</body></html>"
        )
        st.components.v1.html(nk_hero, height=160)
    else:
        st.markdown(clean_html('''
        <div style="background:linear-gradient(135deg,rgba(8,28,8,0.97),rgba(3,10,3,0.99));
        border:1px solid rgba(74,222,128,0.2);border-radius:16px;padding:20px 32px;
        text-align:center;margin-bottom:16px;">
        <div style="font-size:0.65rem;color:#4ade80;text-transform:uppercase;
        letter-spacing:0.22em;font-weight:700;margin-bottom:8px;">Round of 32 Complete</div>
        <div style="font-size:1.2rem;font-weight:800;color:#f0fdf4;">All Round of 32 matches played — follow the bracket below</div>
        </div>'''), unsafe_allow_html=True)
        
    st.markdown("### 🗺️ Visual Bracket Tree")
    render_bracket_tree(ko_live)
    
    render_match_cards(ko_live, get_bracket_data(ko_live))

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — WC WATCHLIST
# ════════════════════════════════════════════════════════════════════════════
with tab_nat:  # WC Watchlist section
    st.markdown('<p class="page-title">📋 World Cup Watchlist</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Top 15% of players per position from the Big 5 leagues heading into the World Cup.</p>', unsafe_allow_html=True)
    wl = df[df["WC_Watchlist_V2"]].copy().sort_values("Overall_Index",ascending=False)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi("Total Scouted",f"{len(wl)}","Top 15% per position"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Avg Age",f"{wl['Age_Years'].mean():.1f} yrs","Squad youth profile"), unsafe_allow_html=True)
    with c3:
        tn=wl["Nation"].value_counts().idxmax()
        st.markdown(kpi("Top Nation",f"{FLAGS.get(tn,'⚽')} {tn}",f"{wl['Nation'].value_counts().max()} players"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Avg Overall",f"{wl['Overall_Index'].mean():.1f}","Out of 100"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔍 Filters", expanded=False):
        _reset = st.button("↺ Reset All Filters", key="wl_reset")
        fc1,fc2,fc3,fc4 = st.columns(4)
        _all_nations = sorted(wl["Nation"].unique())
        _all_leagues = sorted(wl["League"].unique())
        _all_pos = sorted(wl["Primary_Pos"].unique())
        _all_arch = sorted(wl["Archetype_V2"].unique())
        with fc1: sn=st.multiselect("Nations",_all_nations,default=_all_nations,key="wn")
        with fc2: sl=st.multiselect("Leagues",_all_leagues,default=_all_leagues,key="wl2")
        with fc3: sp=st.multiselect("Positions",_all_pos,default=_all_pos,key="wp")
        with fc4: sa=st.multiselect("Archetypes",_all_arch,default=_all_arch,key="wa")
        if _reset:
            st.rerun()
    sq=st.text_input("Search player, club or nation",placeholder="e.g. Bellingham, Arsenal, ENG...",label_visibility="collapsed",key="wsq")
    f=wl[wl["Nation"].isin(sn)&wl["League"].isin(sl)&wl["Primary_Pos"].isin(sp)&wl["Archetype_V2"].isin(sa)]
    if sq: f=f[f["Player"].str.contains(sq,case=False)|f["Squad"].str.contains(sq,case=False)|f["Nation"].str.contains(sq,case=False)]
    if not f.empty:
        st.dataframe(f[["Player","Squad","League","Nation","Primary_Pos","Age_Years","Overall_Index","Attacker_Index","Creator_Index","Defensive_Index","Archetype_V2"]],
            column_config={"Player":st.column_config.TextColumn("Player",width="medium"),"Age_Years":st.column_config.NumberColumn("Age",format="%d yrs",width="small"),
                "Overall_Index":st.column_config.ProgressColumn("Overall",min_value=0,max_value=100,format="%.1f",width="medium"),
                "Attacker_Index":st.column_config.ProgressColumn("Attack",min_value=0,max_value=100,format="%.1f"),
                "Creator_Index":st.column_config.ProgressColumn("Create",min_value=0,max_value=100,format="%.1f"),
                "Defensive_Index":st.column_config.ProgressColumn("Defend",min_value=0,max_value=100,format="%.1f"),
                "Archetype_V2":st.column_config.TextColumn("Archetype",width="medium")},
            use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — HIDDEN GEMS
# ════════════════════════════════════════════════════════════════════════════
with tab_nat:  # Hidden Gems section
    st.markdown('<p class="page-title">💎 Hidden Gems</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Under-24 breakout stars — top 20% of their position, 1,200+ minutes. These are the ones about to blow up.</p>', unsafe_allow_html=True)
    gems=df[df["Hidden_Gem"]].copy().sort_values("Overall_Index",ascending=False)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(kpi("Gems Found",f"{len(gems)}","Age ≤ 24, Min ≥ 1,200"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Avg Age",f"{gems['Age_Years'].mean():.1f} yrs","High ceiling"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Avg Score",f"{gems['Overall_Index'].mean():.1f}","Top tier"), unsafe_allow_html=True)
    with c4:
        t=gems.iloc[0]
        st.markdown(kpi("Top Gem",t["Player"],f"Score: {t['Overall_Index']:.1f}"), unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    vw1,vw2=st.columns([1,4])
    with vw1: view=st.radio("Layout",["Cards 🃏","Table 📋"])
    with vw2:
        with st.expander("🔍 Filters",expanded=False):
            gf1,gf2,gf3,gf4=st.columns(4)
            with gf1: gn=st.multiselect("Nations",sorted(gems["Nation"].unique()),default=sorted(gems["Nation"].unique()),key="ggn")
            with gf2: gl=st.multiselect("Leagues",sorted(gems["League"].unique()),default=sorted(gems["League"].unique()),key="ggl")
            with gf3: gp=st.multiselect("Positions",sorted(gems["Primary_Pos"].unique()),default=sorted(gems["Primary_Pos"].unique()),key="ggp")
            with gf4: ga=st.multiselect("Archetypes",sorted(gems["Archetype_V2"].unique()),default=sorted(gems["Archetype_V2"].unique()),key="gga")
    gsq=st.text_input("Search gems",placeholder="Search...",key="ggsq",label_visibility="collapsed")
    gf=gems[gems["Nation"].isin(gn)&gems["League"].isin(gl)&gems["Primary_Pos"].isin(gp)&gems["Archetype_V2"].isin(ga)]
    if gsq: gf=gf[gf["Player"].str.contains(gsq,case=False)|gf["Squad"].str.contains(gsq,case=False)]
    if gf.empty: st.info("No gems match filters.")
    elif "Cards" in view:
        lim=st.selectbox("Show",[12,24,48,"All"],index=1,key="glim")
        gd=gf if lim=="All" else gf.head(int(lim))
        cards='<div class="card-grid">'
        for _,r in gd.iterrows():
            flag=FLAGS.get(r["Nation"],"⚽")
            cards+=f'''<div class="pcard">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                    <div><p class="pname">{r["Player"]}</p><span class="pbadge">{r["Archetype_V2"]}</span></div>
                    <span style="font-size:1.6rem;">{flag}</span>
                </div>
                <p class="psub">📍 {r["Squad"]} ({r["League"]})</p>
                <div class="pstats">
                    <span class="plabel">Age</span><span class="pval">{int(r["Age_Years"])} yrs</span>
                    <span class="plabel">Position</span><span class="pval">{r["Primary_Pos"]}</span>
                    <span class="plabel">Minutes</span><span class="pval">{int(r["Min"]):,}'</span>
                    <span class="plabel">Overall</span><span class="pscore">{r["Overall_Index"]:.1f}</span>
                </div>
                <div style="margin-top:10px;font-size:0.75rem;border-top:1px dashed rgba(74,222,128,0.08);padding-top:10px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="color:#4b7c4b;">Attack</span><span style="color:#dcfce7;font-weight:600;">{r["Attacker_Index"]:.1f}</span></div>
                    <div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="color:#4b7c4b;">Create</span><span style="color:#dcfce7;font-weight:600;">{r["Creator_Index"]:.1f}</span></div>
                    <div style="display:flex;justify-content:space-between;"><span style="color:#4b7c4b;">Defend</span><span style="color:#dcfce7;font-weight:600;">{r["Defensive_Index"]:.1f}</span></div>
                </div></div>'''
        cards+='</div>'
        st.markdown(clean_html(cards),unsafe_allow_html=True)
    else:
        st.dataframe(gf[["Player","Squad","League","Nation","Primary_Pos","Age_Years","Min","Overall_Index","Attacker_Index","Creator_Index","Defensive_Index","Archetype_V2"]],
            column_config={"Age_Years":st.column_config.NumberColumn("Age",format="%d yrs",width="small"),"Min":st.column_config.NumberColumn("Min",format="%d'",width="small"),
                "Overall_Index":st.column_config.ProgressColumn("Overall",min_value=0,max_value=100,format="%.1f"),
                "Attacker_Index":st.column_config.ProgressColumn("Attack",min_value=0,max_value=100,format="%.1f"),
                "Creator_Index":st.column_config.ProgressColumn("Create",min_value=0,max_value=100,format="%.1f"),
                "Defensive_Index":st.column_config.ProgressColumn("Defend",min_value=0,max_value=100,format="%.1f")},
            use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — PLAYER COMPARISON
# ════════════════════════════════════════════════════════════════════════════
with tab_nat:  # Player Comparison section
    st.markdown('<p class="page-title">⚔️ Player Comparison</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Head-to-head on percentiles and raw stats. Pick any two players.</p>', unsafe_allow_html=True)
    pl=sorted(df["Player"].unique())
    cs1,cs2=st.columns(2)
    with cs1: p1n=st.selectbox("Player 1",pl,index=pl.index("Erling Haaland") if "Erling Haaland" in pl else 0)
    with cs2: p2n=st.selectbox("Player 2",pl,index=pl.index("Kylian Mbappé") if "Kylian Mbappé" in pl else min(1,len(pl)-1))
    p1=df[df["Player"]==p1n].iloc[0]; p2=df[df["Player"]==p2n].iloc[0]
    cc1,cc2=st.columns(2)
    for i,(pr,color,tc) in enumerate([(p1,"#4ade80","#86efac"),(p2,"#fbbf24","#fde68a")]):
        with [cc1,cc2][i]:
            flag=FLAGS.get(pr["Nation"],"⚽")
            st.markdown(clean_html(f'''<div class="pcard" style="border-color:{color}40;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                    <div><p class="pname">{pr["Player"]}</p><span class="pbadge" style="color:{tc};border-color:{color}40;">{pr["Archetype_V2"]}</span></div>
                    <span style="font-size:1.6rem;">{flag}</span>
                </div>
                <p class="psub">📍 {pr["Squad"]} ({pr["League"]})</p>
                <div class="pstats">
                    <span class="plabel">Age</span><span class="pval">{int(pr["Age_Years"])} yrs</span>
                    <span class="plabel">Position</span><span class="pval">{pr["Primary_Pos"]}</span>
                    <span class="plabel">Minutes</span><span class="pval">{int(pr["Min"]):,}'</span>
                    <span class="plabel">Overall</span><span style="font-size:1.5rem;font-weight:800;color:{color};text-align:right;">{pr["Overall_Index"]:.1f}</span>
                </div></div>'''), unsafe_allow_html=True)
    cats=["Attacker Index","Creator Index","Defensive Index","Goals p90","Assists p90","Interceptions p90"]
    v1=[p1[c+"_Pct"] for c in ["Attacker_Index","Creator_Index","Defensive_Index","Gls_p90","Ast_p90","Int_p90"]]
    v2=[p2[c+"_Pct"] for c in ["Attacker_Index","Creator_Index","Defensive_Index","Gls_p90","Ast_p90","Int_p90"]]
    r1=[p1[c] for c in ["Attacker_Index","Creator_Index","Defensive_Index","Gls_p90","Ast_p90","Int_p90"]]
    r2=[p2[c] for c in ["Attacker_Index","Creator_Index","Defensive_Index","Gls_p90","Ast_p90","Int_p90"]]
    cats_c=cats+[cats[0]]; v1_c=v1+[v1[0]]; v2_c=v2+[v2[0]]; r1_c=r1+[r1[0]]; r2_c=r2+[r2[0]]
    fig=go.Figure()
    fig.add_trace(go.Scatterpolar(r=v1_c,theta=cats_c,fill='toself',name=p1["Player"],line_color='#4ade80',fillcolor='rgba(74,222,128,0.12)',customdata=r1_c,hovertemplate="<b>%{theta}</b><br>Pct: %{r:.1f}%<br>Raw: %{customdata:.2f}<extra></extra>"))
    fig.add_trace(go.Scatterpolar(r=v2_c,theta=cats_c,fill='toself',name=p2["Player"],line_color='#fbbf24',fillcolor='rgba(251,191,36,0.12)',customdata=r2_c,hovertemplate="<b>%{theta}</b><br>Pct: %{r:.1f}%<br>Raw: %{customdata:.2f}<extra></extra>"))
    fig.update_layout(polar=dict(bgcolor='rgba(8,28,8,0.3)',radialaxis=dict(visible=True,range=[0,100],gridcolor='rgba(74,222,128,0.08)',tickfont=dict(color='#86efac',size=9)),angularaxis=dict(gridcolor='rgba(74,222,128,0.08)',tickfont=dict(color='#dcfce7',size=11))),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#f0fdf4'),margin=dict(l=40,r=40,t=40,b=40),height=460,showlegend=True,legend=dict(orientation="h",yanchor="bottom",y=1.1,xanchor="center",x=0.5,font=dict(color='#dcfce7')))
    st.plotly_chart(fig,use_container_width=True)
    def crow(label,v1,v2,hi=True,fmt="%.2f"):
        s1,s2=fmt%v1,fmt%v2
        if v1==v2: c1=c2='<td style="padding:10px 14px;color:#dcfce7;text-align:center;">'
        elif (v1>v2 and hi) or (v1<v2 and not hi):
            c1='<td style="padding:10px 14px;color:#4ade80;font-weight:700;text-align:center;">'; c2='<td style="padding:10px 14px;color:#4b7c4b;text-align:center;">'
        else:
            c1='<td style="padding:10px 14px;color:#4b7c4b;text-align:center;">'; c2='<td style="padding:10px 14px;color:#fbbf24;font-weight:700;text-align:center;">'
        t1=" 🏆" if (v1>v2 and hi) or (v1<v2 and not hi) else ""
        t2=" 🏆" if (v2>v1 and hi) or (v2<v1 and not hi) else ""
        return f"<tr><td style='padding:10px 14px;color:#dcfce7;font-weight:500;'>{label}</td>{c1}{s1}{t1}</td>{c2}{s2}{t2}</td></tr>"
    mx=[("Overall 🎖️",p1["Overall_Index"],p2["Overall_Index"],True,"%.1f"),("Attack Index 🏹",p1["Attacker_Index"],p2["Attacker_Index"],True,"%.1f"),("Create Index 🪄",p1["Creator_Index"],p2["Creator_Index"],True,"%.1f"),("Defend Index 🛡️",p1["Defensive_Index"],p2["Defensive_Index"],True,"%.1f"),("Goals p90 ⚽",p1["Gls_p90"],p2["Gls_p90"],True,"%.2f"),("Assists p90 👟",p1["Ast_p90"],p2["Ast_p90"],True,"%.2f"),("G+A p90 🔥",p1["GA_p90"],p2["GA_p90"],True,"%.2f"),("SoT p90 🎯",p1["SoT_p90"],p2["SoT_p90"],True,"%.2f"),("Interceptions p90 🛡️",p1["Int_p90"],p2["Int_p90"],True,"%.2f"),("Crosses p90 📡",p1["Crs_p90"],p2["Crs_p90"],True,"%.2f"),("Minutes ⏱️",p1["Min"],p2["Min"],True,"%d'")]
    tbl=f'<div style="overflow-x:auto;"><table class="ctable"><thead><tr><th>Metric</th><th style="color:#4ade80;text-align:center;">P1: {p1["Player"]}</th><th style="color:#fbbf24;text-align:center;">P2: {p2["Player"]}</th></tr></thead><tbody>'
    for m in mx: tbl+=crow(*m)
    tbl+="</tbody></table></div>"
    st.markdown(clean_html(tbl),unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — NATIONS
# ════════════════════════════════════════════════════════════════════════════
with tab_nat:
    # ── GLOBAL PLAYER SEARCH ───────────────────────────────────────────────
    st.markdown("### 🔍 Player Search")
    search_col, _ = st.columns([2,1])
    with search_col:
        global_search = st.text_input("Search any player, club or nation", 
            placeholder="Try: Bellingham, Arsenal, ENG, Winger...",
            key="global_search", label_visibility="collapsed")
    if global_search and len(global_search) >= 2:
        results = df[df["Player"].str.contains(global_search,case=False,na=False)|
                     df["Squad"].str.contains(global_search,case=False,na=False)|
                     df["Nation"].str.contains(global_search,case=False,na=False)|
                     df["Archetype_V2"].str.contains(global_search,case=False,na=False)].sort_values("Overall_Index",ascending=False)
        if len(results)>0:
            st.markdown(f"**{len(results)} results for '{global_search}'**")
            st.dataframe(results[["Player","Squad","League","Nation","Primary_Pos","Age_Years","Overall_Index","Archetype_V2","Hidden_Gem","WC_Watchlist_V2"]],
                column_config={"Age_Years":st.column_config.NumberColumn("Age",format="%d yrs",width="small"),
                    "Overall_Index":st.column_config.ProgressColumn("Overall",min_value=0,max_value=100,format="%.1f"),
                    "Hidden_Gem":st.column_config.CheckboxColumn("💎 Gem"),
                    "WC_Watchlist_V2":st.column_config.CheckboxColumn("📋 Watchlist")},
                use_container_width=True,hide_index=True)
        else:
            st.info(f"No players found for '{global_search}'")
        st.markdown("---")
    
    st.markdown('<p class="page-title">🌍 Nation Breakdown</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Which countries are sending the strongest talent? Explore national talent pools.</p>', unsafe_allow_html=True)
    def top5_avg(g): return g.nlargest(5).mean()
    dn = df.groupby("Nation")["Overall_Index"].agg(avg=top5_avg, cnt="count").reset_index()
    dn = dn.query("cnt>=2").sort_values("avg",ascending=True).tail(15)
    dn["label"]=dn["Nation"].apply(lambda n: f"{FLAGS.get(n,'⚽')} {n}")
    ch1,ch2=st.columns(2)
    with ch1:
        fn=px.bar(dn,x="avg",y="label",orientation="h",color="avg",color_continuous_scale=[[0,"#064E3B"],[1,"#4ade80"]],labels={"avg":"Avg Overall Score","label":"Nation"})
        fn.update_layout(title=dict(text="Top 15 Nations by Avg Overall Index",font=dict(size=15,color='#f0fdf4')),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#86efac'),xaxis=dict(gridcolor='rgba(74,222,128,0.05)'),yaxis=dict(gridcolor='rgba(74,222,128,0.05)'),margin=dict(l=90,r=20,t=50,b=40),height=460,coloraxis_showscale=False)
        fn.update_traces(hovertemplate="<b>%{y}</b><br>Top-5 Avg: %{x:.1f}<br><i>Click Nations tab → Top 5 per Nation to explore</i><extra></extra>")
        st.plotly_chart(fn,use_container_width=True)
    with ch2:
        dp=df.groupby("Primary_Pos")["Overall_Index"].mean().reset_index().sort_values("Overall_Index",ascending=True)
        fp=px.bar(dp,x="Overall_Index",y="Primary_Pos",orientation="h",color="Overall_Index",color_continuous_scale=[[0,"#064E3B"],[1,"#4ade80"]])
        fp.update_layout(title=dict(text="Avg Overall Index by Position",font=dict(size=15,color='#f0fdf4')),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#86efac'),xaxis=dict(gridcolor='rgba(74,222,128,0.05)'),yaxis=dict(gridcolor='rgba(74,222,128,0.05)'),margin=dict(l=60,r=20,t=50,b=40),height=460,coloraxis_showscale=False)
        st.plotly_chart(fp,use_container_width=True)
    st.markdown("<br>",unsafe_allow_html=True)
    # Dark Horse of the Tournament - belongs here with nations context
    st.markdown("---")
    st.markdown("### 🐴 Dark Horse of WC 2026")
    dh_cols = st.columns(len([k for k in DARK_HORSES.keys() if k != "NOR_backup"]))
    dh_list = [(k,v) for k,v in DARK_HORSES.items() if k != "NOR_backup" and isinstance(v,dict)]
    for col_idx, (dh_code, dh) in enumerate(dh_list[:3]):
        with dh_cols[col_idx]:
            st.markdown(clean_html(f'''<div class="dh-card" style="min-height:220px;">
                <div class="dh-tag">DARK HORSE</div>
                <div style="font-size:1.1rem;font-weight:800;color:#fbbf24;margin-bottom:8px;">{dh["flag"]} {dh.get("name",dh_code)}</div>
                <div style="font-size:0.75rem;color:#86efac;font-weight:700;margin-bottom:8px;text-transform:uppercase;">{dh["tagline"]}</div>
                <div style="font-size:0.82rem;color:#dcfce7;line-height:1.7;">{dh["story"][:200]}...</div>
            </div>'''), unsafe_allow_html=True)

    st.markdown("---")
    nk1,nk2,nk3=st.columns(3)
    with nk1: st.markdown(kpi("Nations Represented",f"{df['Nation'].nunique()}","Across dataset"), unsafe_allow_html=True)
    with nk2: st.markdown(kpi("Nations on Watchlist",f"{df[df['WC_Watchlist_V2']]['Nation'].nunique()}","With ≥1 watchlist player"), unsafe_allow_html=True)
    with nk3:
        bn=dn.iloc[-1]
        st.markdown(kpi("Strongest Pool",f"{FLAGS.get(bn['Nation'],'⚽')} {bn['Nation']}",f"Avg: {bn['avg']:.1f} ({int(bn['cnt'])} players)"), unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.subheader("🏆 Top 5 Players per Nation")
    top_nations=df.groupby("Nation")["Player"].count().sort_values(ascending=False).head(20).index.tolist()
    tabs_n=st.tabs([f"{FLAGS.get(n,'⚽')} {n}" for n in top_nations])
    for tab,nc in zip(tabs_n,top_nations):
        with tab:
            td=df[df["Nation"]==nc].sort_values("Overall_Index",ascending=False).head(5)[["Player","Squad","League","Primary_Pos","Age_Years","Overall_Index","Archetype_V2"]].copy()
            td.insert(0,"Rank",range(1,len(td)+1))
            st.dataframe(td,column_config={"Rank":st.column_config.NumberColumn("Rank",format="#%d",width="small"),"Age_Years":st.column_config.NumberColumn("Age",format="%d yrs",width="small"),"Overall_Index":st.column_config.ProgressColumn("Overall",min_value=0,max_value=100,format="%.1f",width="medium"),"Archetype_V2":st.column_config.TextColumn("Archetype",width="medium")},use_container_width=True,hide_index=True)


# ── FOOTER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:60px;padding:16px 32px;border-top:1px solid rgba(74,222,128,0.06);text-align:center;">
    <div style="font-size:0.65rem;color:#2d4a2d;letter-spacing:0.05em;">
        Built by <a href="https://www.linkedin.com/in/lalith-polikepati" target="_blank" style="color:#3d6b3d;text-decoration:none;font-weight:600;">Lalith Polikepati</a>
        &nbsp;·&nbsp; MS Business Analytics & AI, UTD
        &nbsp;·&nbsp; <a href="https://github.com/p-lalith/kickoff26" target="_blank" style="color:#3d6b3d;text-decoration:none;">GitHub</a>
        &nbsp;·&nbsp; Data: FBref 2024-25
    </div>
</div>
""", unsafe_allow_html=True)
