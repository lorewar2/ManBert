import pandas as pd

# Load your CSV file
df = pd.read_csv("result.csv", header=None)

# Assume:
# column 0 = filename
# column 1 = score
file_to_score = dict(zip(df[0], df[1]))

# Your required order
files = [
"184.txt","51.pdf","144.txt","255.txt","155.txt","130.txt","60.txt","56.pdf","24.pdf","8.pdf","9.pdf",
"109.txt","152.txt","23.pdf","140.txt","229.txt","254.txt","174.txt","27.pdf","189.txt","36.pdf","256.txt",
"63.txt","71.txt","190.txt","7.pdf","58.pdf","503.pdf","505.pdf","465.pdf","342.pdf","378.pdf","691.pdf",
"642.pdf","304.pdf","264.pdf","685.pdf","533.pdf","590.pdf","282.pdf","757.pdf","538.pdf","695.pdf",
"751.pdf","670.pdf","483.pdf","295.pdf","729.pdf","704.pdf","749.pdf","493.pdf","399.pdf","350.pdf",
"766.pdf","328.pdf","486.pdf","531.pdf","354.pdf","355.pdf","384.pdf","312.pdf","768.pdf","666.pdf",
"430.pdf","629.pdf","463.pdf","288.pdf","307.pdf","587.pdf","591.pdf","601.pdf","284.pdf","630.pdf",
"699.pdf","496.pdf","467.pdf","473.pdf","438.pdf","698.pdf","986.pdf","846.pdf","966.pdf","947.pdf",
"795.pdf","831.pdf","929.pdf","981.pdf","945.pdf","920.pdf","788.pdf","819.pdf","952.pdf","1010.pdf",
"870.pdf","865.pdf","1001.pdf","942.pdf","916.pdf","1022.pdf","1006.pdf","775.pdf","917.pdf","796.pdf",
"848.pdf","1015.pdf","852.xml"
]

# Get scores in order (None if missing)
scores = [file_to_score.get(f, None) for f in files]

# Print results
for s in scores:
    print(s)