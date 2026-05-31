import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.graph_objects as go

# 웹페이지 기본 설정 (제목 및 아이콘)
st.set_page_config(page_title="전국 지역축제 효율성 분석", layout="wide")

# 1. 🚨 데이터베이스 파일 존재 여부 체크 (친절한 에러 메시지)
db_filename = "festival.db"

if not os.path.exists(db_filename):
    st.error(f"⚠️ 데이터베이스 파일(`{db_filename}`)을 찾을 수 없습니다.")
    st.info("💡 프로젝트 폴더 안에 SQLite 데이터베이스 파일이 올바르게 위치해 있는지 확인해 주세요.")
    st.stop()  # 파일이 없으면 여기서 프로그램을 안전하게 멈춥니다.

# 2. 데이터베이스 연결 및 SQL 실행
conn = sqlite3.connect(db_filename)

# 공식 행정구역 순서대로 데이터를 가져오는 SQL 쿼리
# '총괄' 데이터인 regional_summary 테이블을 기준으로 안전하게 조회합니다.
query = """
SELECT 
    광역자치단체,
    축제수,
    총방문객수
FROM regional_summary
ORDER BY 
    CASE 광역자치단체
        WHEN '서울' THEN 1 WHEN '부산' THEN 2 WHEN '대구' THEN 3 WHEN '인천' THEN 4 
        WHEN '광주' THEN 5 WHEN '대전' THEN 6 WHEN '울산' THEN 7 WHEN '세종' THEN 8 
        WHEN '경기' THEN 9 WHEN '강원' THEN 10 WHEN '충북' THEN 11 WHEN '충남' THEN 12 
        WHEN '전북' THEN 13 WHEN '전남' THEN 14 WHEN '경북' THEN 15 WHEN '경남' THEN 16 
        WHEN '제주' THEN 17 END;
"""

df = pd.read_sql_query(query, conn)
conn.close()

# 3. 대시보드 화면 꾸미기
st.title("📊 2025 전국 지역별 축제 수 vs 총 방문자 수 분석")
st.markdown("지자체의 축제 공급(양적 투입)과 실제 관광객의 수요(모객력) 간의 미스매치를 분석합니다.")
st.write("---")

# 레이아웃 분할 (상단에 요약 수치 보여주기)
col1, col2, col3 = st.columns(3)
col1.metric("전국 총 축제 수", f"{df['축제수'].sum():,} 개")
col2.metric("전국 총 방문자 수", f"{int(df['총방문객수'].sum()):,} 명")
col3.metric("가장 축제가 많은 지역", f"{df.loc[df['축제수'].idxmax(), '광역자치단체']} ({df['축제수'].max()}개)")

st.write("---")

# ① 시각화: Plotly를 이용한 이중 축 콤보 차트 그리기
fig = go.Figure()

# 왼쪽 Y축: 지역별 축제 수 (막대 차트)
fig.add_trace(
    go.Bar(
        x=df['광역자치단체'],
        y=df['축제수'],
        name="축제 수 (개)",
        marker_color='#87CEEB',
        opacity=0.8,
        yaxis='y1'
    )
)

# 오른쪽 Y축: 연간 총 방문자 수 (선 차트)
fig.add_trace(
    go.Scatter(
        x=df['광역자치단체'],
        y=df['총방문객수'],
        name="총 방문자 수 (명)",
        mode='lines+markers',
        line=dict(color='#FF4500', width=3),
        marker=dict(size=8),
        yaxis='y2'
    )
)

# 이중 축 레이아웃 상세 설정
fig.update_layout(
    title=dict(text="지역별 축제 공급과 수요 미스매치 비교", font=dict(size=18)),
    xaxis=dict(title="광역자치단체 (공식 순서)"),
    yaxis=dict(
        title="축제 수 (개)",
        titlefont=dict(color="navy"),
        tickfont=dict(color="navy"),
        range=[0, 180]
    ),
    yaxis2=dict(
        title="총 방문자 수 (명)",
        titlefont=dict(color="darkred"),
        tickfont=dict(color="darkred"),
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.5)"),
    hovermode="x unified",
    figsize=(12, 6)
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig, use_container_width=True)

st.write("---")

# ② 사용한 SQL 쿼리 보여주기
with st.expander("🔍 분석에 사용된 SQL 데이터 마트 쿼리 보기"):
    st.code(query, language="sql")

# ③ 인사이트 서술
st.subheader("💡 데이터 분석 인사이트")
st.info("""
- **양적 투입의 한계 고발 (공급 과잉 부작용)**: 전남(143개)과 경북(101개)은 축제 수가 최상위권이지만 방문자 수 그래프가 푹 꺼지는 '깊은 골짜기' 형태를 보입니다. 단순히 예산을 쪼개어 축제를 많이 여는 '나눠먹기식 집행'이 모객력으로 직결되지 않음을 증명합니다.
- **고효율 가성비 지역 발굴**: 대전의 경우 축제 수(22개)는 최하위권이지만, 대형 킬러 콘텐츠 중심의 전략적 투자 성과로 방문자 수는 상위권으로 솟구치는 '양적 공급의 질적 역전' 우수 벤치마킹 사례로 볼 수 있습니다.
""")
