#common P3D options
load-display pandagl
textures-power-2 None
win-size 1024 768
show-frame-rate-meter  1
sync-video 0
framebuffer-srgb true
#default-texture-color-space sRGB
texture-minfilter  mipmap
texture-magfilter  linear
#show-buffers 1
#undecorated 1

#koparka specific config
#koparka-filters
# 0 - none 
# 1 - fxaa only
# 2 - all on (screen space soft shadows, glare/flare, etc.)
koparka-filters 2
#render grass? 0=no 1=yes
koparka-use-grass 1
#size of the maps savesd by the editor
koparka-height-map-size 512
koparka-attribute-map-size 512
koparka-grass-map-size 512
koparka-walk-map-size 256
#where to load the data from
koparka-brush-dir "brush/"
koparka-terrain-tex-diffuse-dir "tex/diffuse"
koparka-terrain-tex-normal-dir "tex/normal"
koparka-grass-tex-dir "grass/"
koparka-model-dir "models/"
koparka-walls-dir "models_walls/"
koparka-actors-dir "models_actor/"
koparka-collision-dir "models_collision/"
#default data
koparka-default-height-map "data/def_height.png"
koparka-default-attribute-map "data/atr_def.png"
koparka-default-terrain-mesh "data/mesh80k.bam"
koparka-default-skydome-mesh "data/skydome2"
koparka-default-water-mesh "data/waterplane"
koparka-default-water-tex "data/water.png"
koparka-default-water-wave-tex "data/ocen3.png"
#shadows (what is seen by the shadow casting camera)
koparka-terrain-shadows True
koparka-grass-shadows False
koparka-object-shadows True
#water reflections (what is seen by the water reflection camera)
koparka-terrain-reflection True
koparka-objects-reflection True
koparka-sky-reflection True
koparka-grass-reflection False
#keymap
koparka-key-paint
koparka-key-rotate-r
koparka-key-rotate-l
koparka-key-scale-up
koparka-key-scale-down
koparka-key-alpha-up
koparka-key-alpha-down
koparka-key-next
koparka-key-height-mode
koparka-key-texture-mode
koparka-key-grass-mode
koparka-key-object-mode
koparka-key-walk-mode
koparka-key-config
koparka-key-save
koparka-key-axis-h
koparka-key-axis-p
koparka-key-axis-r
koparka-key-camera-rotate
koparka-key-camera-pan
koparka-key-camera-zoomin
koparka-key-camera-slow
koparka-key-camera-fast
#alt keys
koparka-key-camera-zoomout
koparka-key-camera-rotate2
koparka-key-camera-pan2
koparka-key-camera-zoomin2
koparka-key-camera-zoomout2