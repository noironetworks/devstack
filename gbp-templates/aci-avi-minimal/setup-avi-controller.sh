# upload the avi controller image

# create a port on Service-Management PTG

# use that port to boot avicontroller
glance image-create --name AviController --disk-format qcow2 --container-format bare --file ~/images/controller.qcow2 --progress
sleep 20
