# loops/verify.md — 자동 검증 명령 모음

전부 통과해야 배포한다.

```bash
py -3 build/validate_data.py                 # 단일 진실 원천
py -3 build/validate_xlsx.py                 # 진도표
node build/check_site.js out/site            # 통합 웹사이트

# 12차시 반복
py -3 build/validate_hwpx.py "out/지도안/WISE_L01_지도안.hwpx"
py -3 build/validate_hwpx.py "out/활동지/WISE_L01_활동지.hwpx"
py -3 build/validate_pptx.py "out/ppt/WISE_L01_수업.pptx"
py -3 build/validate_webapp_spec.py "out/webapp/L01"
node build/smoke_webapp.js "out/webapp/L01"
node build/run_webapp.js "out/webapp/L01"
```

전체를 한 번에 돌리려면 :

```bash
py -3 build/verify_all.py
```
