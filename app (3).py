import streamlit as st
import pandas as pd
import sqlite3

# 1. 화면 설정 (웹 페이지 제목)
st.set_page_config(page_title="2025 지역별 축제 통계", layout="wide")

# 2. 데이터베이스 설정 및 가짜 데이터 생성 (SQLite)
def init_db():
    conn = sqlite3.connect('festival_data.db')
    cursor = conn.cursor()
    
    # 테이블 생성 (이미 있으면 생성 안 함)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS festival_stats (
            region TEXT,
            festival_count INTEGER,
            visitor_count INTEGER
        )
    ''')
    
    # 데이터가 비어있을 때만 샘플 데이터 삽입
    cursor.execute("SELECT count(*) FROM festival_stats")
    if cursor.fetchone()[0] == 0:
        # 사진과 유사한 샘플 데이터 (17개 광역자치단체)
        data = [
            ('서울', 71, 17200000), ('부산', 57, 12500000), ('대구', 38, 3500000),
            ('인천', 28, 3200000), ('광주', 19, 2900000), ('대전', 22, 6500000),
            ('울산', 34, 4900000), ('세종', 7, 1000000), ('경기', 155, 14000000),
            ('강원', 123, 11500000), ('충북', 60, 6200000), ('충남', 101, 13400000),
            ('전북', 89, 8200000), ('전남', 143, 10800000), ('경북', 101, 10500000),
            ('경남', 109, 12500000), ('제주', 57, 1500000)
        ]
        cursor.executemany("INSERT INTO festival_stats VALUES (?, ?, ?)", data)
        conn.commit()
    return conn

# 3. 데이터 불러오기
def load_data():
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM festival_stats", conn)
    conn.close()
    return df

# 메인 화면 구성
st.title("📊 2025 지역별 축제 수 vs 연간 총 방문자 수 비교")
st.markdown("공공데이터를 활용한 지역별 축제 현황 대시보드입니다.")

# 데이터 로드
df = load_data()

# 4. 시각화 (이중 축 콤보 차트)
def draw_chart(data):
    # 이중 축을 위한 서브플롯 생성
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 막대 그래프 추가 (지역별 축제 수) - 왼쪽 Y축
    fig.add_trace(
        go.Bar(
            x=data['region'],
            y=data['festival_count'],
            name="축제 수 (개)",
            marker_color='lightblue',
            opacity=0.8
        ),
        secondary_y=False,
    )

    # 선 그래프 추가 (방문자 수) - 오른쪽 Y축
    fig.add_trace(
        go.Scatter(
            x=data['region'],
            y=data['visitor_count'],
            name="총 방문자 수 (명)",
            mode='lines+markers',
            line=dict(color='orangered', width=2),
            marker=dict(size=8)
        ),
        secondary_y=True,
    )

    # 차트 레이아웃 설정
    fig.update_layout(
        title_text="지역별 축제 현황 비교 (2025)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        height=600
    )

    # X축 설정
    fig.update_xaxes(title_text="광역자치단체")

    # 왼쪽 Y축 설정
    fig.update_yaxes(title_text="<b>축제 수 (개)</b>", secondary_y=False, range=[0, 180])

    # 오른쪽 Y축 설정
    fig.update_yaxes(title_text="<b>총 방문자 수 (명)</b>", secondary_y=True, tickformat=",d")

    return fig

# 차트 표시
chart = draw_chart(df)
st.plotly_chart(chart, use_container_width=True)

# 5. 하단 데이터 테이블 표시
with st.expander("원본 데이터 보기"):
    st.dataframe(df, use_container_width=True)
