#!/bin/sh
# ============================================================================
#  นำเข้า seed ระหว่าง migration 009 กับ 010 (รันโดย docker-entrypoint-initdb.d)
#
#  ทำไมต้องมีไฟล์นี้:
#  ``010_electives.sql`` ส่วนที่ 4 เติม ``curriculum_rules.group_code`` ด้วย
#  ``WHERE group_code IS NULL`` และส่วนที่ 6 คิด course_id จาก max() ของตาราง
#  ``courses`` — ทั้งสองอย่างต้องมีข้อมูล seed อยู่ใน DB **ก่อน** 010 รัน
#  ถ้า seed มาทีหลัง (เช่นค่อยมา psql -f เอง) จะได้ DB ที่ตารางครบแต่
#  วิชาในแผน 32 แถวไม่มีหมวดสังกัด → progress รายหมวดกับหน้า /liff เพี้ยน
#
#  ชื่อไฟล์ 009z_ ทำให้ glob ของ entrypoint จัดลำดับไว้หลัง 009_* และก่อน 010_*
#  (เรียงถูกทั้งใน C และ en_US collation)
#
#  seed ไม่ได้อยู่ใน db/migrations เพราะมันไม่ใช่ migration — เป็นข้อมูล
#  ที่ generate จาก scraper (ดู db/export_seed.py) จึง mount แยกไว้ที่ /seed
#  **ห้าม mount ไฟล์ seed ซ้อนเข้าไปใน /docker-entrypoint-initdb.d ตรง ๆ**
#  parent ของมันเป็น :ro → Docker สร้าง mountpoint ใหม่ในนั้นไม่ได้ init จะล้ม
#
#  ไม่มี /seed (เช่นรัน image เปล่า ๆ ไม่ผ่าน compose) = ข้ามเงียบ ๆ ไม่ทำให้ล้ม
#  แต่ถ้ามีไฟล์แล้ว psql ล้ม ต้องให้ init ล้มทั้งชุด (ON_ERROR_STOP + set -e)
#  ดีกว่าได้ DB ที่ข้อมูลหายไปครึ่ง ๆ กลาง ๆ แบบไม่มีใครรู้
#
#  entrypoint ของ postgres จะ ``.`` (source) ไฟล์นี้ถ้าไม่มี exec bit ซึ่งเป็น
#  กรณีปกติของ repo ที่ checkout บน Windows — จึง **ห้ามใช้ exit/return**
#  ในไฟล์นี้ เพราะมันจะพา entrypoint ออกไปด้วย ใช้ if ครอบแทน
# ============================================================================
set -e

if [ -d /seed ]; then
    for seed_file in 002_seed_data.sql 003_curriculum_rules.sql; do
        if [ -f "/seed/$seed_file" ]; then
            echo "009z_seed.sh: นำเข้า $seed_file"
            # PGHOST/PGHOSTADDR ว่าง = บังคับต่อผ่าน unix socket ของเซิร์ฟเวอร์
            # ชั่วคราวที่ entrypoint ยกขึ้นมา (ยังไม่เปิด TCP) เหมือนที่
            # docker_process_sql ของ entrypoint ทำ
            PGHOST= PGHOSTADDR= psql \
                -v ON_ERROR_STOP=1 \
                --username "$POSTGRES_USER" \
                --dbname "$POSTGRES_DB" \
                --no-password \
                --no-psqlrc \
                -f "/seed/$seed_file"
        else
            echo "009z_seed.sh: ไม่พบ /seed/$seed_file — ข้าม"
        fi
    done
else
    echo "009z_seed.sh: ไม่ได้ mount /seed — ข้ามการนำเข้า seed ทั้งหมด"
fi
