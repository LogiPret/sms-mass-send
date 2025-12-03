-- ============================
-- ClickOn – Envoi iMessage/SMS CSV (Universal)
-- With phone priority: mobile > work > home
-- ============================

-- MODE TEST
set modeTest to false
set numeroTest to "+14389266456"

-- Demander le fichier CSV
set csvFile to choose file with prompt "Sélectionne le fichier CSV de la campagne :" of type {"public.comma-separated-values-text", "public.text"}

-- Lire le CSV en texte UTF-8
set csvText to read csvFile as «class utf8»
set csvLines to paragraphs of csvText

if (count of csvLines) < 2 then
	display dialog "Le fichier CSV semble vide ou incomplet (en-tête uniquement)." buttons {"OK"} default button 1
	return
end if

-- ============================
--   ANALYSE DES COLONNES
-- ============================

set headerLine to item 1 of csvLines
set headers to my parseCSVLine(headerLine)

-- Nettoyer les en-têtes
set cleanedHeaders to {}
repeat with h in headers
	set end of cleanedHeaders to my trimText(h)
end repeat

-- Détecter les colonnes importantes
set firstNameCol to my findColumn(cleanedHeaders, {"first name", "firstname", "first", "prénom", "prenom", "given name"})
set lastNameCol to my findColumn(cleanedHeaders, {"last name", "lastname", "last", "nom", "surname", "family name"})

-- Colonnes téléphone séparées (priorité: mobile > work > home)
set mobileCol to my findColumn(cleanedHeaders, {"mobile", "cell", "cellulaire", "cellular", "cell_phone", "mobile_phone"})
set workCol to my findColumn(cleanedHeaders, {"work", "travail", "bureau", "office", "work_phone", "business", "professionnel"})
set homeCol to my findColumn(cleanedHeaders, {"home", "maison", "domicile", "residence", "home_phone", "personnel"})

-- Colonne téléphone générique (fallback)
set phoneCol to my findColumn(cleanedHeaders, {"phone", "telephone", "tel", "téléphone", "numéro", "numero"})

-- Vérifier qu'on a trouvé les colonnes nécessaires
set hasPhoneColumn to (mobileCol > 0 or workCol > 0 or homeCol > 0 or phoneCol > 0)
if firstNameCol is 0 or not hasPhoneColumn then
	set missingCols to ""
	if firstNameCol is 0 then set missingCols to missingCols & "• Prénom (first name)
"
	if not hasPhoneColumn then set missingCols to missingCols & "• Téléphone (phone/mobile/work/home)
"
	
	display dialog "Colonnes manquantes détectées :
" & missingCols & "
Colonnes trouvées dans ton CSV :
" & my joinList(cleanedHeaders, ", ") buttons {"OK"} default button 1
	return
end if

-- Afficher les colonnes détectées
set detectionMsg to "Colonnes détectées :
• Prénom : colonne " & firstNameCol & " (" & item firstNameCol of cleanedHeaders & ")
"
if lastNameCol is not 0 then
	set detectionMsg to detectionMsg & "• Nom : colonne " & lastNameCol & " (" & item lastNameCol of cleanedHeaders & ")
"
else
	set detectionMsg to detectionMsg & "• Nom : non trouvé (optionnel)
"
end if

-- Afficher les colonnes téléphone détectées
set detectionMsg to detectionMsg & "
📱 Colonnes téléphone (priorité: mobile > work > home):
"
if mobileCol > 0 then
	set detectionMsg to detectionMsg & "• Mobile : colonne " & mobileCol & " (" & item mobileCol of cleanedHeaders & ") ✓ PRIORITÉ
"
end if
if workCol > 0 then
	set detectionMsg to detectionMsg & "• Work : colonne " & workCol & " (" & item workCol of cleanedHeaders & ")
"
end if
if homeCol > 0 then
	set detectionMsg to detectionMsg & "• Home : colonne " & homeCol & " (" & item homeCol of cleanedHeaders & ")
"
end if
if phoneCol > 0 and mobileCol is 0 and workCol is 0 and homeCol is 0 then
	set detectionMsg to detectionMsg & "• Phone : colonne " & phoneCol & " (" & item phoneCol of cleanedHeaders & ")
"
end if

display dialog detectionMsg buttons {"Continuer"} default button 1

-- Demander le texte du message
set messageInput to my getMultilineMessage()

-- Fonction pour obtenir un message multi-lignes
on getMultilineMessage()
	set defaultMsg to "Bonjour **PRENOM**,\\n\\nJ'aimerais te poser une question rapide...\\n\\nMerci!"
	
	set theMessage to text returned of (display dialog "Tape ton message.

Variables disponibles :
• **PRENOM** → prénom du client
• **NOM** → nom du client

Pour faire un retour à la ligne, tape \\n
Exemple : Ligne 1\\nLigne 2\\nLigne 3

Ton message :" default answer defaultMsg)
	
	-- Remplacer \\n par de vrais retours à la ligne
	set AppleScript's text item delimiters to "\\n"
	set msgParts to text items of theMessage
	set AppleScript's text item delimiters to linefeed
	set theMessage to msgParts as text
	set AppleScript's text item delimiters to ""
	
	return theMessage
end getMultilineMessage

-- ============================
--   Boucle d'envoi
-- ============================

set successCount to 0
set skipCount to 0
set skippedLines to {}

repeat with i from 2 to count of csvLines
	set lineText to item i of csvLines
	set lineNum to i
	
	-- Tronquer la ligne si trop longue pour l'affichage
	if (length of lineText) > 60 then
		set displayLine to (text 1 thru 60 of lineText) & "..."
	else
		set displayLine to lineText
	end if
	
	if lineText is not "" then
		-- Utiliser le parser CSV robuste
		set fields to my parseCSVLine(lineText)
		
		set maxColNeeded to my maxOf({firstNameCol, lastNameCol, mobileCol, workCol, homeCol, phoneCol})
		
		if (count of fields) ≥ maxColNeeded then
			
			-- Extraire les données
			set firstName to my trimText(item firstNameCol of fields)
			if lastNameCol is not 0 then
				set lastName to my trimText(item lastNameCol of fields)
			else
				set lastName to ""
			end if
			
			-- ============================
			-- SÉLECTION TÉLÉPHONE (priorité: mobile > work > home)
			-- ============================
			set rawPhone to ""
			set phoneSource to ""
			set formattedPhone to ""
			
			-- Mode colonnes séparées (mobile/work/home)
			if mobileCol > 0 or workCol > 0 or homeCol > 0 then
				-- Essayer mobile d'abord
				if mobileCol > 0 and mobileCol ≤ (count of fields) then
					set rawMobile to my trimText(item mobileCol of fields)
					set testPhone to my formatPhoneNumber(rawMobile)
					if testPhone is not "" then
						set formattedPhone to testPhone
						set rawPhone to rawMobile
						set phoneSource to "mobile"
					end if
				end if
				
				-- Si pas de mobile valide, essayer work
				if formattedPhone is "" and workCol > 0 and workCol ≤ (count of fields) then
					set rawWork to my trimText(item workCol of fields)
					set testPhone to my formatPhoneNumber(rawWork)
					if testPhone is not "" then
						set formattedPhone to testPhone
						set rawPhone to rawWork
						set phoneSource to "work"
					end if
				end if
				
				-- Si pas de work valide, essayer home
				if formattedPhone is "" and homeCol > 0 and homeCol ≤ (count of fields) then
					set rawHome to my trimText(item homeCol of fields)
					set testPhone to my formatPhoneNumber(rawHome)
					if testPhone is not "" then
						set formattedPhone to testPhone
						set rawPhone to rawHome
						set phoneSource to "home"
					end if
				end if
			end if
			
			-- Fallback: colonne phone générique
			if formattedPhone is "" and phoneCol > 0 and phoneCol ≤ (count of fields) then
				set rawPhone to my trimText(item phoneCol of fields)
				set formattedPhone to my formatPhoneNumber(rawPhone)
				set phoneSource to "phone"
			end if
			
			-- Valider et envoyer
			if firstName is "" then
				set skipCount to skipCount + 1
				set end of skippedLines to "⚠️ Ligne " & lineNum & " — Prénom vide
   → " & displayLine
			else if formattedPhone is "" then
				set skipCount to skipCount + 1
				set end of skippedLines to "⚠️ Ligne " & lineNum & " — Téléphone invalide (" & rawPhone & ")
   → " & displayLine
			else
				-- Nettoyer le prénom et nom des caractères spéciaux
				set cleanFirstName to my cleanName(firstName)
				set cleanLastName to my cleanName(lastName)
				
				-- Remplacer **PRENOM** dans le message
				set AppleScript's text item delimiters to "**PRENOM**"
				set tmpList to text items of messageInput
				set AppleScript's text item delimiters to cleanFirstName
				set messageText to tmpList as text
				set AppleScript's text item delimiters to ""
				
				-- Remplacer **NOM** dans le message
				set AppleScript's text item delimiters to "**NOM**"
				set tmpList to text items of messageText
				set AppleScript's text item delimiters to cleanLastName
				set messageText to tmpList as text
				set AppleScript's text item delimiters to ""
				
				-- Choisir destinataire
				if modeTest then
					set numeroEnvoi to numeroTest
				else
					set numeroEnvoi to formattedPhone
				end if
				
				-- Envoyer
				set sendResult to my sendiMessage(numeroEnvoi, messageText)
				if sendResult then
					set successCount to successCount + 1
				else
					set skipCount to skipCount + 1
					set end of skippedLines to "❌ Ligne " & lineNum & " — Échec d'envoi (" & phoneSource & ")
   → " & displayLine
				end if
				delay 1 -- Délai réduit pour envoi plus rapide
			end if
		else
			set skipCount to skipCount + 1
			set end of skippedLines to "⚠️ Ligne " & lineNum & " — Pas assez de colonnes
   → " & displayLine
		end if
	end if
end repeat

-- Construire le message de résumé
set summaryMsg to "Campagne terminée ✔︎

✅ Envoyés : " & successCount & "
❌ Ignorés : " & skipCount

if (count of skippedLines) > 0 then
	set summaryMsg to summaryMsg & "

--- Lignes ignorées ---
"
	repeat with skipInfo in skippedLines
		set summaryMsg to summaryMsg & skipInfo & "
"
	end repeat
end if

-- Afficher le dialogue au premier plan
tell application "System Events"
	activate
end tell
delay 0.2
display dialog summaryMsg buttons {"OK"} default button 1 with title "Résultat de la campagne"


-- ============================
--   Handlers
-- ============================

-- Fonction pour nettoyer les noms/prénoms des caractères problématiques
on cleanName(theName)
	if theName is "" then return ""
	
	-- Caractères à supprimer complètement
	set badChars to {",", ";", "\"", "'", "`", "(", ")", "[", "]", "{", "}", "<", ">", "|", "\\", "/", "*", "?", ":", "!", "@", "#", "$", "%", "^", "&", "=", "+", "~"}
	
	set cleanedName to theName
	
	repeat with badChar in badChars
		set AppleScript's text item delimiters to badChar
		set nameParts to text items of cleanedName
		set AppleScript's text item delimiters to ""
		set cleanedName to nameParts as text
	end repeat
	
	-- Nettoyer les espaces multiples
	set AppleScript's text item delimiters to "  "
	repeat while cleanedName contains "  "
		set nameParts to text items of cleanedName
		set AppleScript's text item delimiters to " "
		set cleanedName to nameParts as text
		set AppleScript's text item delimiters to "  "
	end repeat
	set AppleScript's text item delimiters to ""
	
	-- Trim début et fin
	set cleanedName to my trimText(cleanedName)
	
	return cleanedName
end cleanName

on sendiMessage(phoneNumber, messageText)
	-- Envoyer via SMS par défaut - Messages basculera automatiquement vers iMessage si le destinataire l'a
	
	-- Essai 1: Service "SMS" direct
	try
		tell application "Messages"
			send messageText to participant phoneNumber of account "SMS"
		end tell
		return true
	on error errMsg1
		-- Essai 2: Premier service SMS trouvé
		try
			tell application "Messages"
				set smsService to first account whose service type is SMS
				send messageText to participant phoneNumber of smsService
			end tell
			return true
		on error errMsg2
			-- Essai 3: Chercher le service par nom (iPhone)
			try
				tell application "Messages"
					set allServices to every account
					repeat with s in allServices
						try
							if service type of s is SMS then
								send messageText to participant phoneNumber of s
								return true
							end if
						end try
					end repeat
				end tell
			on error errMsg3
				-- Rien ne marche
			end try
			
			display dialog "Erreur d'envoi SMS à " & phoneNumber & "

Vérifie que 'Transfert de SMS' est activé sur ton iPhone:
Réglages → Messages → Transfert de SMS → Active ton Mac

Erreur: " & errMsg2 buttons {"Continuer", "Arrêter"} default button 1
			if button returned of result is "Arrêter" then error number -128
			return false
		end try
	end try
end sendiMessage


on formatPhoneNumber(rawPhone)
	-- Enlever tous les caractères non-numériques sauf le +
	set cleanPhone to ""
	set validChars to "0123456789+"
	
	repeat with c in rawPhone
		if validChars contains c then
			set cleanPhone to cleanPhone & c
		end if
	end repeat
	
	-- Si vide, retourner vide
	if cleanPhone is "" then return ""
	
	-- Si ça commence par +, on garde tel quel (mais vérifier longueur minimale)
	if cleanPhone starts with "+" then
		if (length of cleanPhone) ≥ 11 then
			return cleanPhone
		else
			return ""
		end if
	end if
	
	-- Si ça commence par 1 et a 11 chiffres, ajouter +
	if (length of cleanPhone) is 11 and cleanPhone starts with "1" then
		return "+" & cleanPhone
	end if
	
	-- Si ça a 10 chiffres, ajouter +1
	if (length of cleanPhone) is 10 then
		return "+1" & cleanPhone
	end if
	
	-- Sinon, retourner vide (numéro invalide)
	return ""
end formatPhoneNumber


on findColumn(headerList, possibleNames)
	repeat with i from 1 to count of headerList
		set headerLower to my toLowerCase(item i of headerList)
		repeat with possibleName in possibleNames
			if headerLower contains possibleName then
				return i
			end if
		end repeat
	end repeat
	return 0
end findColumn


on toLowerCase(txt)
	set lowerChars to "abcdefghijklmnopqrstuvwxyzàâäéèêëïîôùûüÿç"
	set upperChars to "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ"
	set newText to ""
	
	repeat with c in txt
		set pos to offset of c in upperChars
		if pos > 0 then
			set newText to newText & character pos of lowerChars
		else
			set newText to newText & c
		end if
	end repeat
	
	return newText
end toLowerCase


on maxOf(numList)
	set maxNum to 0
	repeat with n in numList
		if n > maxNum then set maxNum to n
	end repeat
	return maxNum
end maxOf


on joinList(theList, delimiter)
	set oldDelims to AppleScript's text item delimiters
	set AppleScript's text item delimiters to delimiter
	set theString to theList as string
	set AppleScript's text item delimiters to oldDelims
	return theString
end joinList


on trimText(t)
	set theChars to {" ", tab, return, linefeed}
	set textItemDelimitersBackup to AppleScript's text item delimiters
	
	set AppleScript's text item delimiters to theChars
	set itemList to text items of t
	
	repeat while (count of itemList) > 0 and item 1 of itemList is ""
		if (count of itemList) > 1 then
			set itemList to items 2 thru -1 of itemList
		else
			set itemList to {}
		end if
	end repeat
	
	repeat while (count of itemList) > 0 and item -1 of itemList is ""
		if (count of itemList) > 1 then
			set itemList to items 1 thru -2 of itemList
		else
			set itemList to {}
		end if
	end repeat
	
	set AppleScript's text item delimiters to ""
	if (count of itemList) = 0 then
		set trimmed to ""
	else
		set trimmed to itemList as text
	end if
	set AppleScript's text item delimiters to textItemDelimitersBackup
	return trimmed
end trimText


-- Parser CSV robuste qui gère les virgules dans les guillemets
on parseCSVLine(csvLine)
	set fieldList to {}
	set currentField to ""
	set insideQuotes to false
	set i to 1
	set lineLength to length of csvLine
	
	repeat while i ≤ lineLength
		set currentChar to character i of csvLine
		
		if currentChar is "\"" then
			-- Vérifier si c'est un guillemet échappé ("")
			if i < lineLength and character (i + 1) of csvLine is "\"" then
				-- Guillemet échappé, ajouter un seul guillemet
				set currentField to currentField & "\""
				set i to i + 1
			else
				-- Basculer l'état insideQuotes
				set insideQuotes to not insideQuotes
			end if
		else if currentChar is "," and not insideQuotes then
			-- Fin du champ
			set end of fieldList to currentField
			set currentField to ""
		else
			-- Caractère normal, ajouter au champ
			set currentField to currentField & currentChar
		end if
		
		set i to i + 1
	end repeat
	
	-- Ajouter le dernier champ
	set end of fieldList to currentField
	
	return fieldList
end parseCSVLine
