# This Python file uses the following encoding: utf-8

import es, playerlib, os, sys, time, gamethread, weaponlib, usermsg, popuplib, random, string
from math import sqrt
from threading import Thread

info = es.AddonInfo()
info.name = 'ToCsFreezeMod'
info.version = '0.1'
info.url = 'www.team-tocs.com'
info.basename = 'freezemod'
info.author = 'Sulff'

armes = {}
gunsKills = {}
color = { "3":{}, "2": {} }

color["2"]["c1"] =  255
color["2"]["c2"] =  50
color["2"]["c3"] =  50
color["2"]["alpha"] = 180
color["3"]["c1"] =  0
color["3"]["c2"] =  150
color["3"]["c3"] =  255
color["3"]["alpha"] = 180
                         
# Config
# Choisir entre 100 et 500 hp.
hp = 100

# Coups de cut avant defreeze. (choisir nombre pair)
defreeze = 12

# Argent immédiat que gagne un joueur pour un freeze fait.
argentFreeze = 100

# Pour chaque freeze fait d'affilée, l'argent immédiat que remporte un joueur augmente de x %. Choisir ce pourcentage :
pourcentage = 10

# Bonus qu'accumule un joueur à chaque freeze fait (remporté quand sa team gagne).
argentTeam = 50

# "on" pour définir chaque nombre de kills par arme aléatoirement, "off" pour désactiver.
randomKills = "on"

# Vitesse du grappin (défaut : 1000)
speedHook = 750

# Entrez le chiffre minimum de kills dans randomRange["start"] et le nombre maximal dans randomRange["end"].
randomRange = {}
randomRange["start"] = 1
randomRange["end"] = 3

# Dommages infligé avec la god grenade #

nm_damage = es.ServerVar("nm_damage", 300, "Damage that hegrenade's cause, default = 100")
nm_radius = es.ServerVar("nm_radius", 700, "Radius of hegrenade, default = 350")

# Armes primaires: pour enlever une arme, supprimez les 3 lignes contenant son nom.
# Pour modifier sa valeur d'achat (["cash"] = ) ou le nombre de kill (["kills" = ) à effectuer avec, modifier la valeur correspondante.
# Si randomKills est activé, le nombre de kills à effectuer sera ignoré.

armes["mac10"] = {}
armes["mac10"]["cash"] = 100
armes["mac10"]["kills"] = 1
armes["tmp"] = {}
armes["tmp"]["cash"] = 100
armes["tmp"]["kills"] = 1
armes["ump45"] = {}
armes["ump45"]["cash"] = 100
armes["ump45"]["kills"] = 1
armes["mp5navy"] = {}
armes["mp5navy"]["cash"] = 100
armes["mp5navy"]["kills"] = 1
armes["p90"] = {}
armes["p90"]["cash"] = 250
armes["p90"]["kills"] = 1
armes["m3"] = {}
armes["m3"]["cash"] = 150
armes["m3"]["kills"] = 1
armes["xm1014"] = {}
armes["xm1014"]["cash"] = 200
armes["xm1014"]["kills"] = 1
armes["famas"] = {}
armes["famas"]["cash"] = 230
armes["famas"]["kills"] = 1
armes["galil"] = {}
armes["galil"]["cash"] = 230
armes["galil"]["kills"] = 1
armes["scout"] = {}
armes["scout"]["cash"] = 270
armes["scout"]["kills"] = 1
armes["ak47"] = {}
armes["ak47"]["cash"] = 320
armes["ak47"]["kills"] = 1
armes["m4a1"] = {}
armes["m4a1"]["cash"] = 350
armes["m4a1"]["kills"] = 1
armes["aug"] = {}
armes["aug"]["cash"] = 380
armes["aug"]["kills"] = 1
armes["m249"] = {}
armes["m249"]["cash"] = 450
armes["m249"]["kills"] = 1
armes["awp"] = {}
armes["awp"]["cash"] = 380
armes["awp"]["kills"] = 1
armes["g3sg1"] = {}
armes["g3sg1"]["cash"] = 330
armes["g3sg1"]["kills"] = 1
armes["sg552"] = {}
armes["sg552"]["cash"] = 290
armes["sg552"]["kills"] = 1
armes["sg550"] = {}
armes["sg550"]["cash"] = 440
armes["sg550"]["kills"] = 1

# Armes secondaires : modifier les kills uniquement. (arme non supprimable)
gunsKills["glock"] = 1
gunsKills["usp"] = 1
gunsKills["p228"] = 1
gunsKills["elite"] = 1
gunsKills["fiveseven"] = 1
gunsKills["deagle"] = 1

# Couleurs lors du freeze d'un joueur. (0-255)
# CT :
color["2"]["c1"] =  255
color["2"]["c2"] =  50
color["2"]["c3"] =  50
color["2"]["alpha"] = 180
# Terro
color["3"]["c1"] =  0
color["3"]["c2"] =  150
color["3"]["c3"] =  255
color["3"]["alpha"] = 180
# Arme primaire par défaut
baseWeapon = "mac10"

if randomKills == "on":
    for i in armes:
        armes[i]["kills"] = random.randint(randomRange["start"], randomRange["end"])
    for i in gunsKills:
        gunsKills[i] = random.randint(randomRange["start"], randomRange["end"])

mod = "#green[FreezeMod]#lightgreen"


realhp = 512 + hp
nbCut = {}
joueursEnVie = {}
pointsTeam = {}
spawnTeam = {}
winnerTeam = 0
winners = {}
once = {}
pointsJoueur = {}
couleurJoueur = {}
nbFreeze = {}
killsArme = {}
menuJoueur = {}
autoBuy = {}
secondary = {}
commande = {}
db = {}
oldEntList = {}
vPrepared = []
global grappin
grappin = {}
armes[baseWeapon]["cash"] = 0


listeArmes = []
for i in armes:
    listeArmes.append(i)
listeGuns = []
for i in gunsKills:
    listeGuns.append(i)

    
nbArmes = 0
for i in armes:
    nbArmes += 1
    
nbGuns = 6
sounds = ("godnade.wav", "godnade2.mp3", "hit.wav")


def load():
    es.ServerVar('FreezeMod', info.version, 'by Sulff - www.team-tocs.com').makepublic()
    es.server.queuecmd("mp_friendlyfire 1")
    es.server.queuecmd("mp_startmoney 0")
    es.flags("remove", "notify", "sv_cheats")
    es.doblock('corelib/noisy_on')
    es.regsaycmd('autoswitch', 'freezemod/autoswitch', 'autoswitch')
    es.addons.registerTickListener(tickSticky)
    es.addons.registerTickListener(tickHook)
    okdl()
    if not es.ServerVar("eventscripts_currentmap") == "":
        global godnade
        global beam
        godnade = es.precachemodel("models/holy_grenade/holy_grenade.mdl")
        beam = es.precachemodel("sprites/crystal_beam1.vmt")
        
        


def es_map_start(ev):
    okdl()
    es.server.queuecmd("mp_friendlyfire 1")
    es.server.queuecmd("mp_startmoney 0")
    global godnade
    global beam
    godnade = es.precachemodel("models/holy_grenade/holy_grenade.mdl")
    beam = es.precachemodel("sprites/crystal_beam1.vmt")
def okdl():
    for sound in sounds:
        es.stringtable('downloadables', 'sound/freezemod/%s'%sound)
    es.stringtable('downloadables', 'materials/holy_grenade/holy_grenade.vtf')
    es.stringtable('downloadables', 'materials/holy_grenade/holy_grenade.vmt')
    es.stringtable('downloadables', 'models/holy_grenade/holy_grenade.mdl')
    es.stringtable('downloadables', 'models/holy_grenade/holy_grenade.xbox.vtx')
    es.stringtable('downloadables', 'models/holy_grenade/holy_grenade.vvd')
    es.stringtable('downloadables', 'models/holy_grenade/holy_grenade.sw.vtx')
    es.stringtable('downloadables', 'models/holy_grenade/holy_grenade.phy')
    es.stringtable('downloadables', 'models/holy_grenade/holy_grenade.dx90.vtx')
    es.stringtable('downloadables', 'models/holy_grenade/holy_grenade.dx80.vtx')
    





def objExists(index):
    try:
        if es.getindexprop(index, "CBaseGrenade.m_hThrower") == None: return False
        else: return True
    except: return False



def getOwner(index):
    return es.getuserid(es.getindexprop(index, "CBaseGrenade.m_hThrower"))
        

def tickSticky():
    try:
        global vPrepared, oldEntList
        entList = es.createentitylist("hegrenade_projectile")
        for index in oldEntList:
            if not index in entList: vPrepared.remove(index)
        oldEntList = entList
        for index in entList:
            if not index in vPrepared and objExists(index):
                userid = getOwner(index)
                if es.exists("userid", userid):
                    es.setindexprop(index, "CBaseEntity.m_nModelIndex", godnade)
                    es.setindexprop(index, "CBaseEntity.m_clrRender", -1)
                    vPrepared.append(index)
    except: pass
                   
def unload():
    es.server.cmd("es_xset freezemod_version 0")
    popuplib.delete("buymenu")
    es.doblock('corelib/noisy_off')    
    es.addons.unregisterTickListener(tickSticky)
    es.addons.unregisterTickListener(tickHook)
    es.unregsaycmd('autoswitch')
def player_activate(ev):
    userid = ev['userid']
    popup(userid)
    gamethread.delayed(5, popuplib.send, ("welcomeMenu", userid))
    autoBuy[userid] = {}
    autoBuy[userid]["orWp"] = None
    autoBuy[userid]["dette"] = None
    killsArme[userid] = {}
    for i in armes:
        killsArme[userid][i] = 0
    for i in gunsKills:
        killsArme[userid][i] = 0
    
def hegrenade_detonate(ev):
    soncmd(userid(ev), "godnade2.mp3", 1.0)

    
def player_death(ev):
    es.server.queuecmd("score add %s 1"%userid(ev))
    es.server.queuecmd("est_DeathAdd %s -1"%userid(ev))
    dissolve(userid(ev))

def dissolve(userid):
    wait = 0.06
    es.server.queuecmd('es_give %s env_entity_dissolver'%userid)
    es.server.queuecmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"'%userid)
    es.server.queuecmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"'%userid)
    es.server.queuecmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"'%(userid, random.randint(0, 3)))	
    es.server.queuecmd('es_xfire %s env_entity_dissolver Dissolve'%userid)
    gamethread.delayed(wait, es.server.queuecmd, 'es_xremove env_entity_dissolver')



    
def popup(userid):
    
    menuJoueur[userid] = {}
    menuJoueur[userid][0] = popuplib.create('menuJoueur[%s][0]'%userid)
    menuJoueur[userid][0].addline("Choix de l'arme secondaire (gratuit):")
    menuJoueur[userid][0].addline('->1. Glock')
    menuJoueur[userid][0].addline('->2. Usp')
    menuJoueur[userid][0].addline('->3. P228')
    menuJoueur[userid][0].addline('->4. Elite')
    menuJoueur[userid][0].addline('->5. Fiveseven')
    menuJoueur[userid][0].addline('->6. Deagle')
    menuJoueur[userid][0].addline('->9. Suite')
    menuJoueur[userid][0].addline('->0. Fermer')
    menuJoueur[userid][0].menuselect = guns0
        

    a = 0

    for i in armes:
        a += 1
        multiple = entierSup(float(a), float(7))
        if not popuplib.exists('menuJoueur[%s][%s]'%(userid, multiple)):
            menuJoueur[userid][multiple] = popuplib.create('menuJoueur[%s][%s]'%(userid, multiple))
            menuJoueur[userid][multiple].menuselect = guns
            menuJoueur[userid][multiple].addline("Choix de l'arme primaire:")
            if multiple != 1:
                menuJoueur[userid][multiple].addline("->8. Précédent")
            if (multiple * 7) < nbArmes :
                menuJoueur[userid][multiple].addline("->9. Suite")
            menuJoueur[userid][multiple].addline("->0. Fermer")
        position = int("%s"%(a-((multiple-1)*7)))
        menuJoueur[userid][multiple].insline((position+1), "->%s. %s : %s$"%(position, i, armes[i]["cash"]))
        
    welcomeMenu = popuplib.create('welcomeMenu')
    welcomeMenu.addline("""
Bienvenue sur le FreezeMod !

____________________________
randomKills = %s
----------------------------
\n
Pour connaître les règles et commandes, tape !rules.

---

HF !

"""%randomKills)
    
    rulesMenu = popuplib.create('rules')
    rulesMenu.addline("""
____________________________________________

    Freezemod : règles              Page 1/2
____________________________________________

- Freezez vos ennemis en leur tirant dessus.
- Libérez vos coéquipiers freezés avec votre cut.
- Chaque ennemi freezé vous rapporte de l'argent + un bonus.
- Vous gagnez ce bonus si votre équipe gagne le round.
____________________________
Tapez 1 pour voir la suite.
Tapez 2 pour voir les commandes.
""")
    rulesMenu.addline('->0. Fermer')
    rulesMenu.menuselect = rules

    rulesMenu2 = popuplib.create('rules2')
    rulesMenu2.addline("""
____________________________________________

    Freezemod : règles              Page 2/2
____________________________________________
- L'argent gagné permet d'acheter des armes.
- Chaque arme demande un certains nombre de kills à effectuer.
- Le premier joueur à avoir fait les kills requis avec toutes les armes gagne.
- Celui-ci et son équipe remportent des freezepoints.
- Ceux-ci sont échangeables contres des récompenses fun.
____________________________
Tapez 1 pour voir les commandes.
""")
    rulesMenu2.menuselect = rules

                    
    cmdMenu = popuplib.create('cmd')
    cmdMenu.addline("""
_____________________________________________

    Freezemod : commandes
_____________________________________________

- !buy
Affiche le menu d'armes. Les pistolets sont gratuits, les autres armes payantes.

- autoswitch
Commande indispensable à binder -> bind "touche de votre choix" "say autoswitch"
Fait défiler des armes adaptées niveau argent et kills requis.
Vous pourrez tirer pour valider l'achat ou rechargez pour annuler.
____________________________
""")



    
def rules(userid, choice, name):
    if name == "rules":
        if choice == 1:
            popuplib.send("rules2", userid)
        if choice == 2:
            popuplib.send("cmd", userid)
    elif name == "rules2":
        if choice == 1:
            popuplib.send("cmd", userid)
    popuplib.close(name, userid)



            
def player_spawn(event_var):
    userid = event_var['userid']
    userteam = event_var['es_userteam']
    player = playerlib.getPlayer(userid)
    global hp
    global realhp
    global pointsJoueur
    global pointsTeam
    global listeT
    global listeCT
    global winnerTeam
    global winners
    global joueursEnVie
    global menuJoueur
    if not userid in pointsJoueur:
        pointsJoueur[userid] = 0
    if userid not in once:
        once[userid] = {}
    grappin[userid] = False
    es.setplayerprop(userid, "CCSPlayer.baseclass.m_iHealth", realhp)
    es.fire("%s !self color \"255 255 255\""%(userid))
    joueursEnVie[userid] = userteam
    donnerPoints(event_var)
    nbFreeze[userid] = 0
    spawnTeam[userid] = userteam
    es.server.queuecmd('es_xfire %s func_hostage_rescue kill'% userid)
    es.server.queuecmd('es_xfire %s hostage_entity kill'% userid)
    es.server.queuecmd('es_xfire %s func_bomb_target kill'% userid)
    es.server.queuecmd('es_xfire %s func_buyzone kill'% userid)
    es.server.queuecmd("es_fire %s !self addoutput \"rendermode 1\""%userid)
    es.server.queuecmd("es_fire %s !self alpha 255"%userid)
    if (userteam == "2") or (userteam == "3"):
        origColor(event_var)
    if userid in commande:
        es.server.queuecmd("es_give %s weapon_%s"%(userid, commande[userid]))
        docash(userid, armes[commande[userid]]["cash"], "-")
        del commande[userid]
    onceMsg(userid, "buy", "tell", "%s Tapez #green!buy#lightgreen à tout moment pour choisir une #greenarme."%mod)



def item_pickup(ev):
    if ev['userid'] not in joueursEnVie:
        es.server.queuecmd("est_removeweapon %s weapon_%s"%(ev['userid'], ev['item']))

    
    
def player_say(event_var):
    userid = event_var['userid']
    if (event_var['text'] == "!buy") & (popuplib.isqueued("menuJoueur[%s][0]"%userid, userid) == 0) :
        popuplib.send('menuJoueur[%s][0]'%userid, userid)
    if (event_var['text'] == "!rules") & (popuplib.isqueued("rules", userid) == 0):
        popuplib.send('rules', userid)
               

     
                
def weapon_reload(event_var):
    if autoBuy[event_var['userid']]["dette"] != None:
        userid = event_var['userid']
        player = playerlib.getPlayer(int(userid))
        weapon = player.weapon
        weaponindex = player.get("weaponindex", "%s"%weapon)
        es.server.queuecmd("es_xremove %s"%weaponindex)
        es.give(userid, "weapon_%s"%autoBuy[userid]["orWp"])
        autoBuy[userid]["dette"] = None
        usermsg.hudhint(userid, "Achat annulé.")

        
def weapon_fire(event_var):
    if autoBuy[event_var['userid']]["dette"] != None:
        userid = event_var['userid']
        player = playerlib.getPlayer(userid)
        ammo = player.get('clip', 'primary')
        player.set('clip', ['primary', ammo+1])
        if autoBuy[userid]["orWp"] != event_var['weapon']:
            docash(userid, autoBuy[userid]["dette"])
            autoBuy[userid]["dette"] = None
            usermsg.hudhint(userid, "Achat validé. (%s : %s$)"%(event_var['weapon'], armes[event_var['weapon']]["cash"]))
        else:
            usermsg.hudhint(userid, "Achat annulé (arme identique).")
            autoBuy[userid]["dette"] = None


            
    if event_var["weapon"] == "knife":
        userid = event_var['userid']
        if grappin[userid] == False:
            es.server.cmd("es_xset cible 0")
            es.server.cmd("est_getviewplayer %s cible"%event_var['userid'])
            cible = es.ServerVar('cible')

                    
            #if (cible != 0) and (str(cible) not in joueursEnVie) and (spawnTeam[(cible)] == event_var['es_userteam']):
            if (cible != 0) and (str(cible) not in joueursEnVie) and (spawnTeam[str(cible)] == event_var['es_userteam']):
                
                grappin[userid] = cible
                x, y, z = es.getplayerlocation(cible) 
                #es.setplayerprop(userid, "CCSPlayer.baseclass.localdata.m_vecBaseVelocity", "0,0,140")
                es.fire('%s !self addoutput "gravity -0.01"'%userid)
                x2, y2, z2 = es.getplayerlocation(userid)
                z2 += 10
                
                es.setpos(userid, x2, y2, z2)        
                distX = float(x) - x2
                distY = float(y) - y2
                distZ = float(z) - z2
                es.msg(x)
                es.msg(y)
                es.msg(z)
                
                distance = (distX)**2 + (distY)**2 + (distZ)**2
                distance = sqrt(distance)
                                     

                coef = speedHook/500
                timeout = distance/(550 * coef)

                #es.server.queuecmd("es_effect beam %s,%s,%s %s,%s,%s %s %s 0 0 %s 4 4 1 1 255 255 255 255 0"%(x2, y2, z2, x, y, z+60, beam, beam, timeout))
                gamethread.delayed(0.05, es.server.queuecmd, 'est_PushTo %s %s %s %s %s'%(event_var['userid'], x, y, z, speedHook/distance))





                
                # vitesse de 500 = 550 game units parcourues par sec ;
                # on divise la distance par les game units parcourues en 1 sec pour savoir au bout de combien
                # de temps le joueur arrive à destination, si la vitesse est augmenté on multiplie par le coefficient d'augmentation.
                
                gamethread.delayed(timeout, es.fire, '%s !self addoutput "gravity 1"'%userid)
                gamethread.delayed(timeout, timeoutVar, userid)
            
    if event_var["weapon"] == "hegrenade":
        global nm_userid
        nm_userid = event_var["userid"]
        gamethread.delayed(0.2, setprop)
        es.emitsound("player", nm_userid, "freezemod/godnade.wav", 1.0, 0.3)

def tickHook():
    playerlist = es.createplayerlist()
    for i in playerlist:
        if grappin[str(i)] != False:
                x, y, z = es.getplayerlocation(grappin[str(i)])
                x2, y2, z2 = es.getplayerlocation(str(i))
                z2 += 40
                es.effect("beam", "%s,%s,%s"%(x2, y2, z2), "%s,%s,%s"%(x, y, z+60), beam, beam, 0, 0, 0.1, 4, 4, 1, 1, 255, 255, 255, 255, 0)

def timeoutVar(userid):
    grappin[userid] = False
    

    
def setprop():
    nm_player = es.getplayerhandle(nm_userid)
    nm_entlist = es.createentitylist("hegrenade_projectile")
    nm_string = 0
    nm_entity = 0
    nm_temp = 0
    for nm_temp in nm_entlist:
        nm_string = es.getindexprop(nm_temp, "CBaseGrenade.m_hThrower")
        if nm_string == nm_player:
            nm_entity = nm_temp
    if nm_entity:
        es.setindexprop(nm_entity, "CBaseGrenade.m_flDamage", nm_damage)
        es.setindexprop(nm_entity, "CBaseGrenade.m_DmgRadius", nm_radius)
    

def round_start(event_var):
    global fin
    userid = event_var['userid']
    fin = "off"
    
    #es.fire("%s weapon_c4 Kill"%(userid))#
    
def round_end(event_var):
    global joueursEnVie
    global winnerTeam
    global fin
    if "2" in list(joueursEnVie.values()):
        if "3" in list(joueursEnVie.values()): # on met winnerTeam à "0" s'il y a eu draw #
            winnerTeam = "0"
            usermsg.hudhint("#all", "Personne ne remporte le round !")
    
def player_disconnect(event_var):
    suppr(event_var)


   

    
def player_hurt(event_var):
    userid = event_var['userid']
    weapon = event_var['weapon']
    attacker = event_var['attacker']
    degats = int(event_var['dmg_health'])
    player = playerlib.getPlayer(userid)
    playerhp = player.health
    global joueursEnVie
    global realhp
    if (event_var['es_userteam'] != event_var['es_attackerteam']):
        if degats <= 100:
            lvl = float(degats)/100
        else:
            lvl = 1.0
        soncmd(attacker, "hit.wav", lvl)
    alive = userid in joueursEnVie
    if alive == False:
        es.setplayerprop(userid, "CCSPlayer.baseclass.m_iHealth", realhp)
        global fin
        if (weapon == "knife") & (fin != "on"):
            if event_var['es_attackerteam'] != event_var ['es_userteam']:
                es.server.queuecmd("es_sexec %s kill"%(userid))
                es.server.queuecmd("es_sexec %s kill"%(attacker))
            elif event_var['es_attackerteam'] == event_var['es_userteam']:
                global nbCut
                if not nbCut.has_key(userid):
                    nbCut[userid] = 1
                    changeColor(event_var, "up")
                elif nbCut.has_key(userid):
                    nbCut[userid] = nbCut[userid] + 1
                    changeColor(event_var, "up")
                    if nbCut[userid] == defreeze:
                        es.server.cmd("est_freeze %s 0"%(userid))
                        es.server.queuecmd("es_fire %s !self color \"255 255 255\""%userid)
                        es.server.queuecmd("es_fire %s !self alpha 255"%userid)
                        origColor(event_var)
                        es.server.queuecmd("es_give %s %s"%(userid, secondary[userid]))
                        if userid in commande:
                            es.server.queuecmd("es_give %s weapon_%s"%(userid, commande[userid]))
                            docash(userid, armes[commande[userid]]["cash"], "-")
                            del commande[userid]
                        else:
                            es.server.queuecmd("es_give %s weapon_%s"%(userid, baseWeapon))
                        nbCut[userid] = 0
                        joueursEnVie[userid] = event_var['userteam']
                        
    if alive == True:
        global hp

        if (weapon == "hegrenade") and (event_var['es_userteam'] != event_var['es_attackerteam']):
            if event_var['es_attackerteam'] == "2":
                team = "#t"
            else:
                team = "#ct"
            a = 0
            for i in joueursEnVie:
                if joueursEnVie[i] != event_var['es_userteam']:
                    a += 1
            es.server.queuecmd("est_Health %s + %s"%(team, degats/a))
            es.tell(attacker, "#multi", "%s Tu reçois #green%s#lightgreen hp de %s grâce à la sainte grenade !"%(mod, degats/a, userid))
            #es.msg(attacker, "Attaqueur : %s, team : %s -> %s joueurs en vie, degats victime: %s, chaque joueur recoit %s hp"%(attacker, team, a, degats, degats/a))
        if (weapon == "hegrenade") and (event_var['es_userteam'] == event_var['es_attackerteam']):
            es.setplayerprop(userid, "CCSPlayer.baseclass.m_iHealth", playerhp+degats)
        elif (playerhp <= 512):
            freeze(event_var)


def autoswitch():
    left = -1
    num = 0
    ok = None
    userid = str(es.getcmduserid())
    player = playerlib.getPlayer(int(userid))
    weapon = player.weapon
    weapon = weapon.replace("weapon_","")
    if (weapon != "knife") and (weapon != "hegrenade"):
        weaponindex = player.get("weaponindex", "weapon_%s"%weapon)
    gunsChange = False
    if weapon in listeArmes:
        if autoBuy[userid]["dette"] == None:
            autoBuy[userid]["orWp"] = weapon
        while (killsArme[userid][weapon] >= armes[weapon]["kills"]) or (left < 0):
            num +=1
            weapon = nextWeapon(weapon, num, listeArmes)
            left = wpMoney(userid, weapon)
            if num > nbArmes:
                usermsg.hudhint(userid, "Aucune arme trouvée (pas assez d'argent)")
                ok = False
                autoBuy[userid]["orWp"] = None
                break
        if ok is None :
            autoBuy[userid]["dette"] = left
            es.server.queuecmd("es_xremove %s"%weaponindex)    
            es.give(userid, "weapon_%s"%weapon)
            usermsg.hudhint(userid, "%s : %s$ [%s/%s]"%(weapon, armes[weapon]["cash"], killsArme[userid][weapon], armes[weapon]["kills"]))
            onceMsg(userid, "autoswitch", "tell", "%s Une fois votre choix effectué, tirez pour valider ou rechargez pour annuler."%mod)
                
    elif weapon in listeGuns:
        while (killsArme[userid][weapon] >= gunsKills[weapon]) or (gunsChange == False):
            num +=1
            weapon = nextWeapon(weapon, num, listeGuns)
            gunsChange = True
            if num > nbGuns:
                usermsg.hudhint(userid, "Aucun pistolet ne requiert plus de kills.")
                ok = False
                break
        if ok is None :
            es.server.queuecmd("es_xremove %s"%weaponindex)
            es.give(userid, "weapon_%s"%weapon)
            usermsg.hudhint(userid, "%s [%s/%s]"%(weapon, killsArme[userid][weapon], gunsKills[weapon]))

def player_jump(ev):
    userid = ev['userid']
    #es.fire('%s !self addoutput "gravity 2"'%userid)
    if userid in grappin:
        es.fire('%s !self addoutput "gravity 1"'%userid)
        grappin[userid] = False
    es.setplayerprop(userid, "CCSPlayer.baseclass.localdata.m_vecBaseVelocity", "0,0,100")
    #gamethread.delayed(0.8, es.fire, '%s !self addoutput "gravity 1.0"'%userid)

        
def origColor(ev):
    userid = ev['userid']
    userteam = ev['es_userteam']
    player = playerlib.getPlayer(userid)
    couleurJoueur[userid] = {}
    couleurJoueur[userid]["c1"] = color[userteam]["c1"]
    couleurJoueur[userid]["c2"] = color[userteam]["c2"]
    couleurJoueur[userid]["c3"] = color[userteam]["c3"]
    couleurJoueur[userid]["alpha"] = color[userteam]["alpha"]
    if not userid in commande:
        if not player.get('primary'):
            es.server.queuecmd("es_give %s weapon_%s"%(userid, baseWeapon))
    
def entierSup(a,b): 
    c = a/b
    d = int(a/b)
    if d < c: 
        return (d + 1)
    elif d == c: 
        return d
    
def guns0(userid, choice, name):
    if autoBuy[str(userid)]["dette"] != None:
        autoBuy[str(userid)]["dette"] == None
        es.tell(userid, "Changement d'arme rapide annulé.")
    player = playerlib.getPlayer(userid)

    if not player.get('isdead'):
        if choice in (1, 2, 3, 4, 5, 6):
            if player.get('secondary'):
                es.server.queuecmd("est_removeweapon %s 2"%userid)
            popuplib.send("menuJoueur[%s][1]"%userid, userid)
            if choice == 1:
                es.give("%s weapon_glock"%userid)
            if choice == 2:
                es.give("%s weapon_usp"%userid)
            if choice == 3:
                es.give("%s weapon_p228"%userid)
            if choice == 4:
                es.give("%s weapon_elite"%userid)
            if choice == 5:
                es.give("%s weapon_fiveseven"%userid)
            if choice == 6:
                es.give("%s weapon_deagle"%userid)
        if choice == 9:
            popuplib.send("menuJoueur[%s][1]"%userid, userid)
        if choice == 10:
            popuplib.close("menuJoueur[%s][0]"%userid, userid)
                


        
def guns(userid, choice, name):

    player = playerlib.getPlayer(userid)
    if not player.get('isdead'):
        multiple = int(name[-2:-1])
        if (choice >= 1) and (choice <= 7):
            numeroArme = ((multiple*7)-8)+choice
            nomArme = listeArmes[numeroArme]
            left = wpMoney(userid, nomArme)
            if wpMoney(userid, nomArme) >= 0:
                if player.get('primary'):
                    es.server.queuecmd("est_removeweapon %s 1"%userid)
                if str(userid) in joueursEnVie:
                    docash(str(userid), armes[nomArme]["cash"], "-")
                    es.give("%s weapon_%s"%(userid, nomArme))
                    onceMsg(userid, "bind", "tell", "%s Tapez : bind \"touche\" \"say autoswitch\" dans la console et utilisez la touche choisie pour faire défiler des armes."%mod)
                else:
                    commande[str(userid)] = nomArme
                    onceMsg(str(userid), "reserverArme", "tell", "#green%s #lightgreenréservée. Vous pouvez changer votre choix autant de fois que souhaité."%nomArme, "#green%s #lightgreenréservée."%nomArme)
            else:
                es.tell("%s Vous ne disposez pas d'assez d'argent pour acheter cette arme."%userid)
        if choice == 8:
            popuplib.send("menuJoueur[%s][%s]"%(userid, (multiple-1)), userid)
        if choice == 9:
            popuplib.send("menuJoueur[%s][%s]"%(userid, (multiple+1)), userid)
        if choice == 10:
            popuplib.close("%s"%name, userid)
            



           
def nextWeapon(weapon, num, liste):
    if liste == listeArmes:
        b = nbArmes - 1
    else:
        b = nbGuns - 1
    if liste.index(weapon) + num > b:
        c = (liste.index(weapon) + num) - b
        return liste[c - 1]
    
    else:
        a = liste.index(weapon) + num
        a = liste[a]
        return a
    
def userid(ev):
    userid = ev['userid']
    return userid


def donnerPoints(event_var):
    userid = event_var['userid']
    if not userid in pointsJoueur:
        pointsJoueur[userid] = 0
    if not userid in pointsTeam:
        pointsTeam[userid] = 0
    if userid in spawnTeam:
        if spawnTeam[userid] == event_var['es_userteam']:
            if (event_var['es_userteam'] == winnerTeam) & (pointsTeam[userid] != 0):
                docash(userid, pointsTeam[userid], "+")
                es.tell("%s Ta team a gagné le round précédent : tu remportes ton bonus de %s$!"%(userid, pointsTeam[userid]))
            elif (event_var['es_userteam'] != winnerTeam) & (pointsTeam[userid] != 0):
                es.tell("%s Ta team a perdu le round précédent : tu ne remportes pas ton bonus de %s$!"%(userid, pointsTeam[userid]))
            if userid in pointsTeam:
                pointsTeam[userid] = 0
                
        elif spawnTeam[userid] != event_var['es_userteam']:
            if (event_var['es_userteam'] != winnerTeam) & (pointsTeam[userid] != 0):
                docash(userid, pointsTeam[userid], "+")
                es.tell("%s Ta team précédente a gagné le round : tu remportes ton bonus de %s$!"%(userid, pointsTeam[userid]))
            elif (event_var['es_userteam'] == winnerTeam) & (pointsTeam[userid] != 0):
                es.tell("%s Ta team précédente a perdu le round : tu ne remportes pas ton bonus de %s$!"%(userid, pointsTeam[userid]))
            if userid in pointsTeam:
                pointsTeam[userid] = 0
                
    docash(userid, pointsJoueur[userid])
    
def suppr(event_var):
    userid = event_var['userid']
    global joueursEnVie
    global pointsTeam
    if userid in joueursEnVie:
        del joueursEnVie[userid]
    if userid in pointsTeam:
        del pointsTeam[userid]

    
def docash(userid, amount, sign=None):

    if sign == "+":
        newcash = pointsJoueur[userid] + amount
        pointsJoueur[userid] = newcash
        es.setplayerprop(userid, "CCSPlayer.m_iAccount", newcash)
    elif sign == "-":
        newcash = pointsJoueur[userid] - amount
        pointsJoueur[userid] = newcash
        es.setplayerprop(userid, "CCSPlayer.m_iAccount", newcash)
    else:
        newcash =  amount
        pointsJoueur[userid] = newcash
        es.setplayerprop(userid, "CCSPlayer.m_iAccount", newcash)
        
#2#
def onceMsg(userid, name, Type, text, second=None):

    if not name in once[userid]:
        text2 = text
    elif (name in once[userid]):
        text2 = second
    if text2 != None:
        if Type == "msg":
            es.msg("#multi", text2)
        elif Type == "tell":
            es.tell(userid, "#multi", text2)
        elif Type == "hudhint":
            usermsg.hudhint(userid, text2)
        once[userid][name] = "on"

#3#
def wpMoney(userid, arme):

    arme2 = arme
    if "weapon_" in arme:
        arme2 = arme.string("weapon_")
    player = playerlib.getPlayer(userid)
    cashArme = armes[arme2]["cash"]
    cashJoueur = pointsJoueur[str(userid)]
    varMoney = cashJoueur - cashArme
    return varMoney

def radiusMatch(event_var):
    userid = event_var['userid']
    attacker = event_var['attacker']
    joueur1 = es.getplayerlocation(userid)
    joueur2 = es.getplayerlocation(attacker)
    radiusMax = 200
    xMax = int(joueur1[0]) - int(joueur2[0])
    yMax = int(joueur1[1]) - int(joueur2[1])
    zMax = int(joueur1[2]) - int(joueur2[2])
    es.msg("%s %s %s"%(xMax, yMax, zMax))
    if ((xMax >= 0) & (xMax <= radiusMax)) or ((xMax < 0) & (xMax > -radiusMax)):
        xMax = 1
    else:
        xMax = 0
    if ((yMax >= 0) & (yMax <= radiusMax)) or ((yMax < 0) & (yMax > -radiusMax)):
        yMax = 1
    else:
        yMax = 0
    if ((zMax >= 0) & (zMax <= radiusMax)) or ((zMax < 0) & (zMax > -radiusMax)):
        zMax = 1
    else:
        zMax = 0
    radiusResultat = (xMax + yMax + zMax)
    #if (xMax + yMax + zMax) == 3#
        
def freeze(event_var):
    userid = event_var['userid']
    attacker = event_var['attacker']
    pUserid = playerlib.getPlayer(userid)
    secondary[userid] = pUserid.get('secondary')
    pAttacker = playerlib.getPlayer(attacker)
    attackerID = pAttacker.steamid
    attackerArme = pAttacker.weapon
    if (attackerArme != "knife") and (attackerArme != "weapon_hegrenade"):
        attackerArme = attackerArme.replace("weapon_","")
    global hp
    global realhp
    global joueursEnVie
    global pointsJoueur
    global pointsTeam
    global winnerTeam
    global killsArme
    es.ServerCommand("est_freeze %s 1"%(userid))
    es.ServerCommand("est_shake %s 0.3 5 1"%(userid))
    es.ServerCommand("est_stripplayer %s 1"%(userid))
    
    es.fire("%s !self DispatchEffect WaterSurfaceExplosion"%(userid))
    es.setplayerprop(userid, "CCSPlayer.baseclass.m_iHealth", realhp)
    del joueursEnVie[userid]
    nbFreeze[userid] = 0
    nbFreeze[attacker] = nbFreeze[attacker] + 1
    #team = []#
    #playerlist = es.createplayerlist()#
    #for i in playerlist:#
        #if str(i) in joueursEnVie:#
            #team.append(playerlist[i]["teamid"])#
    
    #test = int(event_var['es_userteam']) in team#
    
    if event_var['es_userteam'] in list(joueursEnVie.values()):
        changeColor(event_var, "down")

    
    if event_var['es_userteam'] not in list(joueursEnVie.values()):
        if (fin != "on"):
            winnerTeam = event_var['es_attackerteam']
            if winnerTeam == "2":
                usermsg.centermsg("#all", "Les terros remportent le round !")
            else:
                usermsg.centermsg("#all", "Les CT remportent le round !")
            for i in spawnTeam:
                if (spawnTeam[i] == event_var['es_userteam']):
                    es.server.queuecmd("es_sexec %s Kill"%(i))


            global fin
            fin = "on"
    if event_var['es_userteam'] != event_var['es_attackerteam']:
        rab = argentFreeze + ((nbFreeze[attacker]) * (argentFreeze/pourcentage))
        docash(attacker, rab, "+")
        pointsTeam[attacker] = pointsTeam[attacker] + argentTeam
        if (attackerArme in gunsKills) or (attackerArme in armes):
            killsArme[attacker][attackerArme] += 1
        if attackerArme in gunsKills:
            if killsArme[attacker][attackerArme] <= gunsKills[attackerArme]:
                if attackerArme == "glock":
                    menuJoueur[attacker][0].modline(2, '->1. Glock %s/%s'%(killsArme[attacker][attackerArme], gunsKills["glock"]))
                if attackerArme == "usp":
                    menuJoueur[attacker][0].modline(3, '->2. Usp %s/%s'%(killsArme[attacker][attackerArme], gunsKills["usp"]))
                if attackerArme == "p228":
                    menuJoueur[attacker][0].modline(4, '->3. P228 %s/%s'%(killsArme[attacker][attackerArme], gunsKills["p228"]))
                if attackerArme == "elite":
                    menuJoueur[attacker][0].modline(5, '->4. Elite %s/%s'%(killsArme[attacker][attackerArme], gunsKills["elite"]))
                if attackerArme == "fiveseven":
                    menuJoueur[attacker][0].modline(6, '->5. Fiveseven %s/%s'%(killsArme[attacker][attackerArme], gunsKills["fiveseven"]))
                if attackerArme == "deagle":
                    menuJoueur[attacker][0].modline(7, '->6. Deagle %s/%s'%(killsArme[attacker][attackerArme], gunsKills["deagle"]))
        a = 0
        b = 0
        if attackerArme in armes:
            if killsArme[attacker][attackerArme] <= armes[attackerArme]["kills"]:
                c = listeArmes.index(attackerArme) + 1
                multiple = entierSup(float(c),float(7))
                position = int("%s"%(c-((multiple-1)*7)))
                menuJoueur[attacker][multiple].modline((position+1), "->%s. %s : %s$ - %s/%s"%(position, attackerArme, armes[attackerArme]["cash"], killsArme[attacker][attackerArme], armes[attackerArme]["kills"]))



            if attackerArme in armes:
                if killsArme[attacker][attackerArme] >= armes[attackerArme]["kills"]:
                    for i in armes:
                        if i in killsArme[attacker]:
                            if killsArme[attacker][i] >= armes[i]["kills"]:
                                a += 1
                            else:
                                break
            if attackerArme in gunsKills:
                if killsArme[attacker][attackerArme] >= gunsKills[attackerArme]:
                    for i in gunsKills:
                        if i in killsArme[attacker]:
                            if killsArme[attacker][i] >= gunsKills[i]:
                                b += 1
                        else:
                            break
                        
         #if (a == nbArmes) & (b == 6):
        if not attackerID in db:
            db[attackerID] = 0
        db[attackerID] += 90

        playerlist = es.createplayerlist()
        for i in playerlist:
            myPlayer = playerlib.getPlayer(i)
            myteam = myPlayer.teamid
            mysteamID = myPlayer.steamid
            if str(myteam) == event_var['es_attackerteam']:

                if not mysteamID in db:
                    db[mysteamID] = 0
                db[mysteamID] += 30
            #es.msg(db)#
            #team.append(playerlist[i]["teamid"])
            #db = open("dbpoints.txt", "a")
            #db.write("%s 90"%attackerID)
                                                                    
        onceMsg(attacker, "argentkill", "tell", "%s Astuce : #lightgreenl'argent gagné augmente pour chaque ennemi tué d'affilée sans avoir été freezé entre temps."%mod)
        es.server.queuecmd("score add %s 1"%attacker)
        es.server.queuecmd("est_DeathAdd %s 1"%userid)



def hudhint(event_var):
    es.usermsg("create", "hudhint", "HintText")
    es.usermsg("write", "byte", "hudhint", -1)
    es.usermsg("write", "string", "hudhint", "Bonus à remporter : %s"%(pointsTeam[attacker]))
    es.usermsg("send", "hudhint", attacker, "0")
    es.usermsg("delete", "hudhint")

def endround():
    es.server.cmd("sv_cheats 1")
    es.server.cmd("endround")
    es.server.cmd("sv_cheats 0")
 
    
def changeColor(event_var, sens):
    userid = event_var['userid']
    userteam = event_var['es_userteam']
    global color
    global couleurJoueur
    if sens == "down":
        a = 0
        p1, p2, p3, pA = 255, 255, 255, 255
        while a < 3:
            global p1, p2, p3, pA
            a += 0.1
            calcColor(userid, color[userteam]["c1"], color[userteam]["c2"], color[userteam]["c3"], color[userteam]["alpha"], a)

        gamethread.delayedname(3.1, userid, es.server.queuecmd, "es_xfire %s !self color \"%s %s %s\""%(userid, color[userteam]["c1"], color[userteam]["c2"], color[userteam]["c3"]))
        gamethread.delayedname(3.1, userid, es.server.queuecmd, "es_fire %s !self alpha %s"%(userid, color[userteam]["alpha"]))
                
    if sens == "up":
        couleurJoueur[userid]["c1"] += int(((255 - color[userteam]["c1"]) / defreeze))
        couleurJoueur[userid]["c2"] += int(((255 - color[userteam]["c2"]) / defreeze))
        couleurJoueur[userid]["c3"] += int(((255 - color[userteam]["c3"]) / defreeze))
        couleurJoueur[userid]["alpha"] += int(((255 - color[userteam]["alpha"]) / defreeze))
        es.server.queuecmd("es_fire %s !self color \"%s %s %s\""%(userid, couleurJoueur[userid]["c1"], couleurJoueur[userid]["c2"], couleurJoueur[userid]["c3"]))
        es.server.queuecmd("es_fire %s !self alpha %s"%(userid, couleurJoueur[userid]["alpha"]))


        
def calcColor(userid, color1, color2, color3, alpha, a):
    global p1, p2, p3, pA
    p1 -= int(((255-color1)/30))
    p2 -= int(((255-color2)/30))
    p3 -= int(((255-color3)/30))
    pA -= int(((255-alpha)/30)) 
    gamethread.delayedname(a, userid, es.server.queuecmd, "es_xfire %s !self color \"%s %s %s\""%(userid, p1, p2, p3))
    gamethread.delayedname(a, userid, es.server.queuecmd, "es_fire %s !self alpha %s"%(userid, pA))
    
def soncmd(user, son, lvl=1.0):
    es.playsound(user, "freezemod/%s"%son, lvl)







        
