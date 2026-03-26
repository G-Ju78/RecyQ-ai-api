import math

# [기능 1] 시스템에 등록된 공식 수거 거점 목록을 불러오는 함수
def get_disposal_sites():
    # 현재는 테스트를 위해 광주 봉선동 특정 좌표가 입력되어 있음
    # 실제 운영 시에는 MySQL DB에서 수거함 위치 데이터를 받아오는 역할로 확장됨 
    return [{"id": 1, "lat": 35.1325, "lon": 126.9123}] 

# [기능 2] 사용자의 현재 위치가 수거함 반경(20m) 이내인지 검증하는 함수 
def is_within_range(user_lat, user_lon, limit_meter=20):
    """
    user_lat: 앱에서 전송된 사용자의 위도
    user_lon: 앱에서 전송된 사용자의 경도
    limit_meter: 허용 오차 범위 (기본값 20m) 
    """
    
    sites = get_disposal_sites() # 등록된 모든 수거 거점 목록을 가져옴
    R = 6371000 # 지구의 반지름 (단위: 미터, 거리 계산을 위한 상수)
    
    for loc in sites:
        # 1. 위도와 경도의 차이를 구하고, 계산을 위해 '라디안(Radian)' 단위로 변환
        dlat = math.radians(loc['lat'] - user_lat)
        dlon = math.radians(loc['lon'] - user_lon)
        
        # 2. 하버사인(Haversine) 공식 적용: 두 지점 사이의 구면 거리를 구하는 수식
        # a는 두 지점 사이의 직선 현의 길이의 절반의 제곱과 관련된 값
        a = math.sin(dlat/2)**2 + \
            math.cos(math.radians(user_lat)) * \
            math.cos(math.radians(loc['lat'])) * \
            math.sin(dlon/2)**2
            
        # 3. c는 호의 중심각(라디안)을 계산
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # 4. 최종 거리(distance) 계산 = 지구 반지름 * 중심각
        distance = R * c
        
        # [검증] 계산된 거리가 설정된 제한 범위(20m) 이내인지 확인
        if distance <= limit_meter:
            # 범위 안이라면 '성공(True)'과 '실제 거리'를 반환
            return True, distance
            
    # 모든 거점을 확인했는데도 범위 안이 없다면 '실패(False)' 반환
    return False, 0