#Variables:=DefultValues
NEW_DT_NAME:=new_dt

.PHONY: new_dt
new_dt:
	mkdir -p dt/$(NEW_DT_NAME)
	cp -R templates/dt_template/* dt/$(NEW_DT_NAME)/
	pushd dt/$(NEW_DT_NAME)/ && ./render.sh && rm -f render.sh
