from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
load_dotenv()
API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
transport = RequestsHTTPTransport(
    url=API_URL,
    headers={
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    },
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# GraphQL
query = gql("""
query theExamResults($documentId: ID!) {
  exam(documentId: $documentId) {
    exam_results_connection {
      nodes {
        documentId
        student {
          name
        }
        note
      }
    }
  }
}
""")

variables = {
    "documentId": "llj88x09c953yvrbxxpsfquk"
}

try:
    result = client.execute(query, variable_values=variables)
    nodes = result["exam"]["exam_results_connection"]["nodes"]
    students = [{"Öğrenci": n["student"]["name"], "Not": n["note"]} for n in nodes]
    df = pd.DataFrame(students)
except Exception as e:
    print("Veri işlenemedi:", e)
    df = pd.DataFrame(columns=["Öğrenci", "Not"])

# Veri analizi ve grafik
if not df.empty:
    ortalama = np.mean(df["Not"])
    max_not = np.max(df["Not"])
    min_not = np.min(df["Not"])

    print(f"Ortalama Not: {ortalama:.2f}")
    print(f"En Yüksek Not: {max_not}")
    print(f"En Düşük Not: {min_not}")

    df["Durum"] = np.where(df["Not"] >= 60, "Geçti", "Kaldı")

    def harf_notu(not_degeri):
        if not_degeri >= 85:
            return "A"
        elif not_degeri >= 70:
            return "B"
        elif not_degeri >= 60:
            return "C"
        elif not_degeri >= 50:
            return "D"
        else:
            return "F"

    df["Harf Notu"] = df["Not"].apply(harf_notu)
    df["Üstün Başarı"] = np.where(df["Not"] >= ortalama + 10, "Evet", "Hayır")

    print(df)

    plt.bar(df["Öğrenci"], df["Not"], color="skyblue")
    plt.axhline(y=ortalama, color='r', linestyle='--', label='Ortalama')
    plt.title("Öğrenci Notları")
    plt.xlabel("Öğrenci")
    plt.ylabel("Not")
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("Grafiği gösterecek veri bulunamadı.")
