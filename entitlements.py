import pandas as pd
from decimal import Decimal
import streamlit as st

# Load the CSV file
data = pd.read_csv('BAH_WITH_DEPENDENTS.csv')
data1 = pd.read_csv('BAH_WITHOUT_DEPENDENTS.csv')
base_pay_data = pd.read_csv('2023 Active Duty Pay Chart.csv')


def format_rank(rank: str):
  if rank[1:].isdigit() and len(
      rank) == 2:  # If the rank is of the form "EX" or "WX" or "OX"
    return rank[0] + '0' + rank[1], rank[0] + '-' + rank[
      1]  # Returns "E0X", "E-X" or "W0X", "W-X" or "O0X", "O-X"
  else:
    return rank


def check_bas(rank, entitlements):
  if rank.startswith('E'):
    expected_bas = 452.56
  else:
    expected_bas = 311.68

  if entitlements['BAS'] != expected_bas:
    st.write(
      f"Your current BAS is: {entitlements['BAS']}, but it should be: {expected_bas}. There might be something wrong with your BAS. Please check your BAS."
    )


def format_years(years):
  years = int(years)
  if years <= 2:
    formatted_years = "2 or less"
  elif years % 2 != 0:  # if years is odd
    formatted_years = f"Over {years - 1}"  # use the previous even year
  else:  # if years is even
    formatted_years = f"Over {years}"
  return formatted_years


def check_pay(entitlements, rank, years, mha):
  base_pay_str = base_pay_data[base_pay_data['rank'] == format_rank(rank)[1]][
    format_years(years)].values[0]
  base_pay = Decimal(base_pay_str.replace(',', '').replace('$', ''))
  base_pay = base_pay.quantize(Decimal('.01'))
  #base_pay = round(float(base_pay_data[base_pay_data['rank'] == format_rank(rank)[1]][
  #format_years(years)].values[0]), 2)

  bah = data[data['MHA'] == mha][format_rank(rank)[0]].values[0]
  bah_without_dependents = data1[data1['MHA'] == mha][format_rank(rank)
                                                      [0]].values[0]

  if entitlements['BAH'] != bah and entitlements[
      'BAH'] != bah_without_dependents:
    st.write(
      f"Your current BAH is: {entitlements['BAH']} however you should be getting: {bah} with dependents or {bah_without_dependents} without dependents. There might be something wrong with your BAH. Please check your BAH."
    )

  if abs(entitlements['BASE PAY'] - float(base_pay)) > 0.10:
    st.write(
      f"Your current base pay is: {entitlements['BASE PAY']} however you should be getting: {base_pay}. There might be something wrong with your base pay. Please check your base pay."
    )

  check_bas(rank, entitlements)


# check_pay(entitlements)
