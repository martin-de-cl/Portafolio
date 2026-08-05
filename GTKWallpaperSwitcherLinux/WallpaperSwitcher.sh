#!/bin/bash

# 				GTK Gretter Swapper Randomizer - v1.0
#
# 	Small Script to randomly refresh GTK login screen. It's aimed to be used with
# 	systemsmd-sleep feature so it'll run on sleep/suspend signal.
#
#	This is a soft swapper as is doesn't need super user permission. To complete
#	the complete process you need to point you Greeter Wallpaper to the final path
#	by default is pointed to users /home/.themes directory.
#	Add the path to your 
#
# 	@Author: Martín Pimentel Tarbuskovic
#	@Date  : 2019_05_26

finalWallpaperPath='~/.themes'
WallpaperPath=''

function main {

	newWallpaper=$( ls "$WallpaperPath" | sort -R | tail -n 1 )

	if [[ $newWallpaper =~ "jpg" ]] || [[ $newWallpaper =~ "jpeg" ]]; then
		cp "$WallpaperPath$newWallpaper" "$finalWallpaperPath/greeter-paper.jpg"
	else
		convert "$WallpaperPath$newWallpaper" "$finalWallpaperPath/greeter-paper.jpg"
	fi
}

case $1 in 
	pre)
		main
	;;
esac
