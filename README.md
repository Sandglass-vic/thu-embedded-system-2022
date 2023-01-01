# thu-embedded-system-2022
1. 配置buildroot：自行修改config/configs/raspberrypi3_defconfig、config/board/raspberrypi3/linux.config等。**!!! 最好不要修改config目录结构或者raspberrypi3_defconfig文件名!!!**
2. wifi连接：根据raspberrypi3_defconfig中自定义的rootfs_overlay路径(默认为config/board/raspberrypi3/rootfs_overlay)，修改roots_overlay/etc/wpa_supplicant.conf，填入wifi名称和密码。
3. 部署应用：将应用复制到rootfs_overlay目录下，如rootfs_overlay/root。
4. 在README.md同级目录下clone buildroot仓库。
5. 构建系统：建议使用linux环境。运行build.sh即可，构建时长约1~2h。
6. 运行实验：构建完成后将build/images/sdcard.img烧录到SD卡中，并SD卡插入树莓派。树莓派启动后可以ssh登陆，运行你的应用。

Sean
2023/1/1