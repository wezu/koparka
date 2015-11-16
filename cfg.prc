#common P3D options
load-display pandagl
textures-power-2 None
win-size 1024 768
#win-size 1280 720
show-frame-rate-meter  1
sync-video 0
framebuffer-srgb true
#default-texture-color-space sRGB
#textures-srgb true
texture-minfilter  mipmap
texture-magfilter  linear
show-buffers 0
#undecorated 1
#pstats-gpu-timing true

#koparka specific config
#koparka-filters
# 0 - none
# 1 - fxaa only
# 2 - all on (screen space soft shadows, glare/flare, etc.)
# currently all but "2" are broken (?)
koparka-filters 2
#render grass? 0=no 1=yes
koparka-use-grass 1
#size of the maps savesd by the editor
koparka-height-map-size 512
koparka-attribute-map-size 512
koparka-grass-map-size 512
koparka-walk-map-size 256
#where to load the data from
koparka-brush-dir brush/
koparka-terrain-tex-diffuse-dir tex/diffuse/
koparka-terrain-tex-normal-dir tex/normal/
koparka-grass-tex-dir grass/
koparka-model-dir models/
koparka-walls-dir models_walls/
koparka-actors-dir models_actor/
koparka-collision-dir models_collision/
#default data
koparka-default-height-map data/def_height.png
koparka-default-attribute-map data/atr_def.png
koparka-default-terrain-mesh data/mesh80k.bam
#koparka-default-terrain-mesh data/big_mesh.egg
koparka-default-skydome-mesh data/skydome2
koparka-default-water-mesh data/waterplane
koparka-default-water-tex data/water.png
koparka-default-water-wave-tex data/ocen3.png
#shaders
# _v is for vertex shader
#_f is for fragment shader
#these shaders are all GLSL, if you want to use Cg... em.. don't
koparka-shader-terrain_v shaders/terrain_v.glsl
koparka-shader-terrain_f shaders/terrain_f.glsl
koparka-shader-terrain_tc 
koparka-shader-terrain_tes 
koparka-shader-terrain_geo 
#terrain shader that shows the walkmap
koparka-shader-terrain_w_v shaders/terrain_v.glsl
koparka-shader-terrain_w_f shaders/terrain_w_f.glsl
#the 'editor' shader is used for drawing the pointer
koparka-shader-editor_v shaders/editor_v.glsl
koparka-shader-editor_f shaders/editor_f.glsl
koparka-shader-water_v shaders/water_v.glsl
koparka-shader-water_f shaders/water_f.glsl
koparka-shader-grass_v shaders/grass_v.glsl
koparka-shader-grass_f shaders/grass_f.glsl
koparka-shader-sky_v shaders/cloud_v.glsl
koparka-shader-sky_f shaders/cloud_f.glsl
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
koparka-key-paint mouse1
koparka-key-rotate-r e
koparka-key-rotate-l q
koparka-key-scale-up d
koparka-key-scale-down a
koparka-key-alpha-up w
koparka-key-alpha-down s
koparka-key-next tab
koparka-key-prev backspace
koparka-key-height-mode f1
koparka-key-texture-mode f2
koparka-key-grass-mode f3
koparka-key-object-mode f4
koparka-key-walk-mode f5
koparka-key-config f6
koparka-key-save f7
koparka-key-axis-h 1
koparka-key-axis-p 2
koparka-key-axis-r 3
koparka-key-camera-rotate mouse2
koparka-key-camera-pan mouse3
koparka-key-camera-zoomin wheel_up
koparka-key-camera-zoomout wheel_down
koparka-key-camera-slow alt
koparka-key-camera-fast control
#alt keys
koparka-key-camera-rotate2 control
koparka-key-camera-pan2 alt
koparka-key-camera-zoomin2 =
koparka-key-camera-zoomout2 -
#gui theme
koparka-gui-theme icon
#select by using a color in a 1x1 texture buffer 
#slow and not working at the moment
koparka-gl-select False
