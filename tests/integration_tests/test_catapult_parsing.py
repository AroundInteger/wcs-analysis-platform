#!/usr/bin/env python3
"""
Test script to verify Catapult filename parsing improvements
"""

import re
import os

def extract_player_info_from_filename(filename: str) -> dict:
    """
    Extract player information from filename following various patterns
    """
    try:
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        print(f"Testing filename: {name_without_ext}")
        
        # Pattern 1: position_initials_competition(matchday) - e.g., BR_EC_18s(MD2).csv
        pattern1 = r'^([A-Z]+)_([A-Z]+)_([A-Za-z0-9]+)\(([A-Z0-9]+)\)$'
        match1 = re.match(pattern1, name_without_ext)
        
        if match1:
            position, initials, competition, matchday = match1.groups()
            print(f"Pattern 1 matched: {position}, {initials}, {competition}, {matchday}")
            return {
                'position': position,
                'initials': initials,
                'competition': competition,
                'matchday': matchday,
                'player_name': initials,
                'filename_pattern': 'position_initials_competition(matchday)'
            }
        
        # Pattern 2: initials_competition(matchday) - e.g., JR_URC(MD4).csv
        pattern2 = r'^([A-Z]+)_([A-Za-z0-9]+)\(([A-Z0-9]+)\)$'
        match2 = re.match(pattern2, name_without_ext)
        
        if match2:
            initials, competition, matchday = match2.groups()
            print(f"Pattern 2 matched: {initials}, {competition}, {matchday}")
            return {
                'position': 'Unknown',
                'initials': initials,
                'competition': competition,
                'matchday': matchday,
                'player_name': initials,
                'filename_pattern': 'initials_competition(matchday)'
            }
        
        # Pattern 3: position_initials_competition - e.g., FR_JR_URC.csv
        pattern3 = r'^([A-Z]+)_([A-Z]+)_([A-Za-z0-9]+)$'
        match3 = re.match(pattern3, name_without_ext)
        
        if match3:
            position, initials, competition = match3.groups()
            print(f"Pattern 3 matched: {position}, {initials}, {competition}")
            return {
                'position': position,
                'initials': initials,
                'competition': competition,
                'matchday': 'Unknown',
                'player_name': initials,
                'filename_pattern': 'position_initials_competition'
            }
        
        # Pattern 4: Catapult format - Name_Date_Raw Data Date MD vs Opponent
        # e.g., Aaron Ramsey_2024-09-09_Raw Data 09.09.24 MD vs Montenegro.csv
        pattern4 = r'^([A-Za-z\s]+)_(\d{4}-\d{2}-\d{2})_Raw Data \d{2}\.\d{2}\.\d{2} MD vs ([A-Za-z\s]+)$'
        match4 = re.match(pattern4, name_without_ext)
        
        if match4:
            player_name, date, opponent = match4.groups()
            print(f"Pattern 4 matched: {player_name}, {date}, {opponent}")
            return {
                'position': 'Unknown',
                'initials': player_name.split()[0] if player_name else 'Unknown',
                'competition': opponent.strip(),
                'matchday': 'MD',
                'player_name': player_name.strip(),
                'filename_pattern': 'catapult_name_date_opponent'
            }
        
        # Pattern 5: Catapult export format with competition - COMPETITION Export for Name ID
        # e.g., HUNGARY (AWAY) MD1 Export for Alfie Cunningham 27993.csv
        pattern5 = r'^([A-Z\s\(\)]+)\s+Export for ([A-Za-z\s]+) \d+$'
        match5 = re.match(pattern5, name_without_ext)
        
        if match5:
            competition, player_name = match5.groups()
            print(f"Pattern 5 matched: {competition}, {player_name}")
            # Extract matchday from competition if present
            matchday = 'Unknown'
            if 'MD' in competition:
                md_match = re.search(r'MD(\d+)', competition)
                if md_match:
                    matchday = f"MD{md_match.group(1)}"
            
            return {
                'position': 'Unknown',
                'initials': player_name.split()[0] if player_name else 'Unknown',
                'competition': competition.strip(),
                'matchday': matchday,
                'player_name': player_name.strip(),
                'filename_pattern': 'catapult_export_competition_name'
            }
        
        # Pattern 6: Catapult export format - Export for Name ID (generic)
        # e.g., 3A-NT-GP-LSG-10x10-70x60 Export for Michael Obafemi 22346.csv
        pattern6 = r'^.*Export for ([A-Za-z\s]+) \d+$'
        match6 = re.match(pattern6, name_without_ext)
        
        if match6:
            player_name = match6.group(1)
            print(f"Pattern 6 matched: {player_name}")
            return {
                'position': 'Unknown',
                'initials': player_name.split()[0] if player_name else 'Unknown',
                'competition': 'Unknown',
                'matchday': 'Unknown',
                'player_name': player_name.strip(),
                'filename_pattern': 'catapult_export_name'
            }
        
        print("No pattern matched")
        # If no pattern matches, return basic info
        return {
            'position': 'Unknown',
            'initials': 'Unknown',
            'competition': 'Unknown',
            'matchday': 'Unknown',
            'player_name': name_without_ext,
            'filename_pattern': 'unknown'
        }
        
    except Exception as e:
        print(f"Error parsing filename '{filename}': {str(e)}")
        return {
            'position': 'Unknown',
            'initials': 'Unknown',
            'competition': 'Unknown',
            'matchday': 'Unknown',
            'player_name': filename,
            'filename_pattern': 'error'
        }

# Test the problematic Catapult filenames
test_files = [
    "HUNGARY (AWAY) MD1 Export for Alfie Cunningham 27993.csv",
    "ICELAND MD Export for Alfie Tuck 27677.csv",
    "3A-NT-GP-LSG-10x10-70x60 Export for Michael Obafemi 22346.csv",
    "BR_EC_18s(MD2).csv",
    "Aaron Ramsey_2024-09-09_Raw Data 09.09.24 MD vs Montenegro.csv"
]

print("Testing Catapult filename parsing improvements:")
print("=" * 60)

for filename in test_files:
    print(f"\nTesting: {filename}")
    result = extract_player_info_from_filename(filename)
    print(f"Result: Player={result['player_name']}, Competition={result['competition']}, Matchday={result['matchday']}")
    print("-" * 50) 