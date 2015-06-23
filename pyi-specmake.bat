@echo on
pyi-makespec.exe ^
    --log-level=INFO ^
    --specpath=newspec ^
    --additional-hooks-dir=pyi-hooks ^
    --noupx ^
    --noconsole ^
    ConsumerCheck\cc_start.py
