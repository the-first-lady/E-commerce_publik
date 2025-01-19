
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import locale
import requests
import zipfile 
import io
from babel.numbers import format_currency

# Unduh file .zip dari GitHub 
url = 'https://github.com/the-first-lady/E-commerce_publik/raw/main/all_data_ecommerce.zip' 
response = requests.get(url) 
with zipfile.ZipFile(io.BytesIO(response.content)) as z: 
    z.extractall() 
    
# Baca file CSV yang diekstrak dan gunakan dalam aplikasi Streamlit 
data = pd.read_csv('all_data_ecommerce.csv') 
data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])

# Menambahkan header untuk dashboard 
st.title('Dashboard Interaktif') 

# Menambahkan filter tanggal
min_date = data['order_purchase_timestamp'].min()
max_date = data['order_purchase_timestamp'].max()
start_date, end_date = st.sidebar.date_input("Pilih Rentang waktu :", [min_date, max_date], min_value=min_date, max_value=max_date)

# Menambahkan logo ke sidebar 
#st.sidebar.image("C:/Users/USER/Project_Python/Dicoding/proyek_analisis_data/dashboard/E-Commerce-Logo-PNG-Clipart-Background.png")
st.sidebar.image("E-Commerce-Logo-PNG-Clipart-Background.png")

# Menambahkan judul di tengah pada sidebar
st.sidebar.markdown(
    """
    <div style="text-align: center;">
        <h2>E-Commerce Publik</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Memfilter data berdasarkan input pengguna
filtered_data = data[
    (data['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
    (data['order_purchase_timestamp'] <= pd.to_datetime(end_date)) 
]

# Membuat kolom untuk visualisasi Jumlah order, Jumlah produk, Jumlah pembayaran
#col1, col2, col3 = st.columns(3) 
col1, col2, col3, col4 = st.columns(4)

# Jumlah order 
with col1: 
    st.write('Jumlah Order :') 
    order_count = filtered_data['order_id'].nunique()  
    #st.subheader(f'{order_count} pcs')
    st.markdown(f'<p style="font-size:20px;">{order_count} </p>', unsafe_allow_html=True)

# Jumlah produk 
with col2: 
    st.write('Jumlah Produk :') 
    product_count = filtered_data['product_id'].nunique()
    #st.subheader(f'{product_count} pcs')
    st.markdown(f'<p style="font-size:20px;">{product_count} </p>', unsafe_allow_html=True)

# Jumlah seller 
with col3: 
    st.write('Jumlah Seller:') 
    seller_count = filtered_data['seller_id'].nunique() 
    #st.subheader(f'{seller_count}') 
    st.markdown(f'<p style="font-size:20px;">{seller_count} </p>', unsafe_allow_html=True)

# Jumlah pembayaran 
with col4: 
    st.write('Jumlah Revenue :') 
    payment_count = filtered_data['payment_value'].sum() 
    if pd.notnull(payment_count): 
        formatted_payment_count = format_currency(payment_count, 'USD', locale='en_US') 
    else: 
        formatted_payment_count = "N/A"
        
    #st.subheader(formatted_payment_count)
    st.markdown(f'<p style="font-size:20px;">{formatted_payment_count} </p>', unsafe_allow_html=True)

filtered_df = data[(data['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & (data['order_purchase_timestamp'] <= pd.to_datetime(end_date))]

# Buat DataFrame untuk jumlah order harian 
daily_orders = filtered_df.resample('D', on='order_purchase_timestamp').size().reset_index(name='order_count')

# Visualisasikan data
#fig, ax = plt.subplots()
#ax.plot(daily_orders['order_purchase_timestamp'], daily_orders['order_count'], marker='o', linestyle='-')
#ax.set_xlabel('Tanggal')
#ax.set_ylabel('Jumlah Order')
#ax.set_title('Jumlah Order Harian Berdasarkan Rentang Waktu')
# Putar label sumbu x agar vertikal 
#plt.xticks(rotation=45)
#st.pyplot(fig)

# Visualisasi data jumlah order harian berdasarkan rentang waktu yang dipilih 
#with col1: 
    #st.write('Jumlah Order Harian:') 
daily_orders = filtered_data.resample('D', on='order_purchase_timestamp').size().reset_index(name='order_count') 
fig, ax = plt.subplots() 
ax.plot(daily_orders['order_purchase_timestamp'], daily_orders['order_count'], marker='o', linestyle='-') 
ax.set_xlabel('Tanggal') 
ax.set_ylabel('Jumlah Order') 
ax.set_title('Jumlah Order Harian') 
plt.xticks(rotation=90)
st.pyplot(fig) 

# Visualisasi data jumlah revenue berdasarkan rentang waktu yang dipilih 
#with col2: 
    #st.write('Jumlah Revenue Harian:') 
daily_revenue = filtered_data.resample('D', on='order_purchase_timestamp').sum()['payment_value'].reset_index(name='daily_revenue') 
fig, ax = plt.subplots() 
ax.bar(daily_revenue['order_purchase_timestamp'], daily_revenue['daily_revenue'], color=sns.color_palette('colorblind')) 
ax.set_xlabel('Tanggal') 
ax.set_ylabel('Jumlah Revenue') 
ax.set_title('Jumlah Revenue Harian') 
plt.xticks(rotation=90)
st.pyplot(fig)

# Hitung nilai Recency, Frequency, dan Monetary 
current_date = filtered_df['order_purchase_timestamp'].max() 
filtered_df['order_purchase_timestamp'] = pd.to_datetime(filtered_df['order_purchase_timestamp']) 

rfm_data = filtered_df.groupby('customer_id').agg({ 
    'order_purchase_timestamp': lambda x: (current_date - x.max()).days, 
    'customer_id': 'count', 
    'payment_value': 'sum' 
}).reset_index(drop=True) 

rfm_data.columns = ['Recency', 'Frequency', 'Monetary']

st.subheader("Best Customers Based on RFM Parameters")

# Hitung rata-rata RFM
average_recency = round(sum(rfm_data['Recency']) / len(rfm_data['Recency']), 2) 
average_frequency = round(sum(rfm_data['Frequency']) / len(rfm_data['Frequency']), 2) 
average_monetary = round(sum(rfm_data['Monetary']) / len(rfm_data['Monetary']), 2)

# Membuat kolom untuk Tampilkan nilai rata-rata RFM menggunakan widget metric
col1, col2, col3 = st.columns(3) 

# Average Recency 
with col1: 
    st.metric(label="Average Recency", value=average_recency)

#Average Frequency 
with col2:  
    st.metric(label="Average Frequency", value=average_frequency)

#Average Monetary 
with col3:  
    st.metric(label="Average Monetary", value=f"${average_monetary:,.2f}")

# Visualisasi data RFM
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

# Visualisasi Recency
ax[0].bar(range(len(rfm_data['Recency'])), rfm_data['Recency'], color=sns.color_palette('colorblind'))
ax[0].set_title('Recency')
ax[0].set_xlabel('Customer')
ax[0].set_ylabel('Days')

# Visualisasi Frequency
ax[1].bar(range(len(rfm_data['Frequency'])), rfm_data['Frequency'], color=sns.color_palette('colorblind'))
ax[1].set_title('Frequency')
ax[1].set_xlabel('Customer')
ax[1].set_ylabel('Purchases')

# Visualisasi Monetary
ax[2].bar(range(len(rfm_data['Monetary'])), rfm_data['Monetary'], color=sns.color_palette('colorblind'))
ax[2].set_title('Monetary')
ax[2].set_xlabel('Customer')
ax[2].set_ylabel('Amount')

st.pyplot(fig)


# Visualisasi 5 Produk 
product_sales = filtered_df.groupby('product_category_name_english').size().reset_index(name='sales_count')

top_5_products = product_sales.nlargest(5, 'sales_count')
bottom_5_products = product_sales.nsmallest(5, 'sales_count')

st.subheader('Top 5 and Bottom 5 Products')

fig, ax = plt.subplots(1, 2, figsize=(15, 5))

# Visualisasi 5 Produk Terbanyak Terjual
ax[0].bar(top_5_products['product_category_name_english'], top_5_products['sales_count'], color=sns.color_palette('colorblind'))
ax[0].set_title('5 Top Products')
ax[0].set_xlabel('Kategori Produk')
ax[0].set_ylabel('Jumlah Penjualan')
ax[0].tick_params(axis='x', rotation=45)

# Visualisasi 5 Produk Tersedikit Terjual
ax[1].bar(bottom_5_products['product_category_name_english'], bottom_5_products['sales_count'], color=sns.color_palette('colorblind'))
ax[1].set_title('5 Bottom Products')
ax[1].set_xlabel('Kategori Produk')
ax[1].set_ylabel('Jumlah Penjualan')
plt.xticks(rotation=45)

st.pyplot(fig)

# Hitung Jumlah Penjualan untuk Setiap Kota dan Negara:
city_sales = filtered_df.groupby('customer_city').size().reset_index(name='sales_count')
country_sales = filtered_df.groupby('customer_state').size().reset_index(name='sales_count')

# Dapatkan Top 5 Kota dan Negara dengan pembelian Terbanyak
top_5_cities = city_sales.nlargest(5, 'sales_count')
top_5_countries =country_sales.nlargest(5, 'sales_count')

st.subheader('5 Consumer Demographics with the Highest Purchases')

fig, ax = plt.subplots(1, 2, figsize=(15, 5))

# Visualisasi Top 5 Kota dengan pembelian Terbanyak
ax[0].bar(top_5_cities['customer_city'], top_5_cities['sales_count'], color=sns.color_palette('colorblind'))
ax[0].set_title('Customer City')
ax[0].set_xlabel('Kota')
ax[0].set_ylabel('Jumlah Pembelian')
ax[0].tick_params(axis='x', rotation=45)

# Visualisasi Top 5 Negara dengan pembelian Terbanyak
ax[1].bar(top_5_countries['customer_state'], top_5_countries['sales_count'], color=sns.color_palette('colorblind'))
ax[1].set_title('Customer State')
ax[1].set_xlabel('Negara')
ax[1].set_ylabel('Jumlah Pembelian')
ax[1].tick_params(axis='x', rotation=0)

st.pyplot(fig)

# Dapatkan 5 Kota dan Negara dengan Pembelian Terendah
bottom_5_cities = city_sales.nsmallest(5, 'sales_count')
bottom_5_countries = country_sales.nsmallest(5, 'sales_count')

st.subheader('5 Consumer Demographics with the Lowest Purchases')

fig, ax = plt.subplots(1, 2, figsize=(15, 5))

# Visualisasi 5 Kota dengan Pembelian Terendah
ax[0].bar(bottom_5_cities['customer_city'], bottom_5_cities['sales_count'], color=sns.color_palette('colorblind'))
ax[0].set_title('Customer City')
ax[0].set_xlabel('Kota')
ax[0].set_ylabel('Jumlah Pembelian')
ax[0].tick_params(axis='x', rotation=45)

# Visualisasi 5 Negara dengan Penjualan Terendah
ax[1].bar(bottom_5_countries['customer_state'], bottom_5_countries['sales_count'], color=sns.color_palette('colorblind'))
ax[1].set_title('Customer State')
ax[1].set_xlabel('Negara')
ax[1].set_ylabel('Jumlah Pembelian')
ax[1].tick_params(axis='x', rotation=0)

st.pyplot(fig)

# Hitung Jumlah Penjualan untuk Setiap Kota dan Negara
city_sales = filtered_df.groupby('seller_city').size().reset_index(name='sales_count')
country_sales = filtered_df.groupby('seller_state').size().reset_index(name='sales_count')

# Dapatkan Top 5 Kota dan Negara dengan Penjualan Tertinggi:
top_5_cities = city_sales.nlargest(5, 'sales_count')
top_5_countries = country_sales.nlargest(5, 'sales_count')

st.subheader('5 Seller Demographics with the Highest Sales')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Visualisasi Top 5 Kota dengan Penjualan Tertinggi
ax1.bar(top_5_cities['seller_city'], top_5_cities['sales_count'], color=sns.color_palette('colorblind'))
ax1.set_title('Seller City')
ax1.set_xlabel('Kota')
ax1.set_ylabel('Jumlah Penjualan')
ax1.tick_params(axis='x', rotation=45)

# Visualisasi Top 5 Negara dengan Penjualan Tertinggi
ax2.bar(top_5_countries['seller_state'], top_5_countries['sales_count'], color=sns.color_palette('colorblind'))
ax2.set_title('Seller State')
ax2.set_xlabel('Negara')
ax2.set_ylabel('Jumlah Penjualan')
ax2.tick_params(axis='x', rotation=0)

st.pyplot(fig)

# Dapatkan Top 5 Kota dan Negara dengan Penjualan Terendah:
top_5_cities = city_sales.nsmallest(5, 'sales_count')
top_5_countries = country_sales.nsmallest(5, 'sales_count')

st.subheader('5 Seller Demographics with the Lowest Sales')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Visualisasi Top 5 Kota dengan Penjualan Terendah
ax1.bar(top_5_cities['seller_city'], top_5_cities['sales_count'], color=sns.color_palette('colorblind'))
ax1.set_title('Seller City')
ax1.set_xlabel('Kota')
ax1.set_ylabel('Jumlah Penjualan')
ax1.tick_params(axis='x', rotation=45)

# Visualisasi Top 5 Negara dengan Penjualan Terendah
ax2.bar(top_5_countries['seller_state'], top_5_countries['sales_count'], color=sns.color_palette('colorblind'))
ax2.set_title('Seller State')
ax2.set_xlabel('Negara')
ax2.set_ylabel('Jumlah Penjualan')
ax2.tick_params(axis='x', rotation=0)

st.pyplot(fig)

# Buat layout tiga kolom 
col1, col2, col3 = st.columns(3)

# Fungsi untuk membuat bar chart 
def create_bar_chart(data, column, title): 
    fig, ax = plt.subplots() 
    data[column].value_counts().plot.bar(ax=ax, color=sns.color_palette('colorblind')) 
    ax.set_title(title) 
    ax.set_xlabel(column) 
    ax.set_ylabel('Count') 
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

# Buat bar chart untuk review score di kolom pertama 
with col1: 
    st.write('Review Score Distribution')
    create_bar_chart(filtered_df, 'review_score', 'Review Score Distribution')
    
# Buat bar chart untuk payment type di kolom kedua 
with col2: 
    st.write('Payment Type Distribution')
    create_bar_chart(filtered_df, 'payment_type', 'Payment Type Distribution')

# Buat bar chart untuk order status di kolom ketiga 
with col3: 
    st.write('Order Status Distribution')
    create_bar_chart(filtered_df, 'order_status', 'Order Status Distribution')
