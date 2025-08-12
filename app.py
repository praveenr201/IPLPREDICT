from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Load and preprocess data
df = pd.read_csv('ipl_2025_full_predictions.csv')
df = df.dropna()

# Label Encoding
all_teams = pd.concat([df['Team1'], df['Team2']]).unique()
le = LabelEncoder()
le.fit(all_teams)

df['Team1_encoded'] = le.transform(df['Team1'])
df['Team2_encoded'] = le.transform(df['Team2'])

# Features and label
feature_cols = ['Team1_encoded', 'Team2_encoded',
                'Team1_Total_Wins_vs_Team2', 'Team2_Total_Wins_vs_Team1',
                'Team1_Venue_Wins', 'Team2_Venue_Wins',
                'Team1_Current_Standing', 'Team2_Current_Standing',
                'Team1_Estimated_Win_Probability(%)', 'Team2_Estimated_Win_Probability(%)']

X = df[feature_cols]
y = (df['Team1_Estimated_Win_Probability(%)'] > df['Team2_Estimated_Win_Probability(%)']).astype(int)

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Lookup dictionary
team_name_to_encoded = dict(zip(le.classes_, le.transform(le.classes_)))

# Prediction API
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    team1 = data.get('team1')
    team2 = data.get('team2')

    if not team1 or not team2 or team1 == team2:
        return jsonify({'error': 'Invalid team selection.'}), 400

    try:
        team1_enc = team_name_to_encoded[team1]
        team2_enc = team_name_to_encoded[team2]

        match = df[((df['Team1'] == team1) & (df['Team2'] == team2)) |
                   ((df['Team1'] == team2) & (df['Team2'] == team1))]

        if match.empty:
            return jsonify({'error': 'Match data not found.'}), 404

        match = match.iloc[0]

        if match['Team1'] != team1:
            team1_enc, team2_enc = team2_enc, team1_enc

        features = {
            'Team1_encoded': team1_enc,
            'Team2_encoded': team2_enc,
            'Team1_Total_Wins_vs_Team2': match['Team1_Total_Wins_vs_Team2'],
            'Team2_Total_Wins_vs_Team1': match['Team2_Total_Wins_vs_Team1'],
            'Team1_Venue_Wins': match['Team1_Venue_Wins'],
            'Team2_Venue_Wins': match['Team2_Venue_Wins'],
            'Team1_Current_Standing': match['Team1_Current_Standing'],
            'Team2_Current_Standing': match['Team2_Current_Standing'],
            'Team1_Estimated_Win_Probability(%)': match['Team1_Estimated_Win_Probability(%)'],
            'Team2_Estimated_Win_Probability(%)': match['Team2_Estimated_Win_Probability(%)'],
        }

        input_df = pd.DataFrame([features])
        prediction = model.predict(input_df)

        winner = team1 if prediction[0] == 1 else team2
        return jsonify({'winner': winner})

    except KeyError:
        return jsonify({'error': 'Invalid team name(s).'}), 400

if __name__ == '__main__':
    app.run(debug=True)
