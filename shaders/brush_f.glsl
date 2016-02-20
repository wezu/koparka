//GLSL
#version 140
uniform sampler2D p3d_Texture0;
uniform sampler2D map;
uniform float use_map;
uniform vec4 brush_color;
in vec4 color;
in vec2 uv;
in vec2 map_uv;
void main() 
    {        
    vec4 brush=brush_color*texture2D(p3d_Texture0, uv)*(1.0-use_map); 
    
    float sharpness=brush_color.a*0.01;
    vec4 blur = texture2D(map, map_uv+vec2( -0.326212, -0.405805)*sharpness);
    blur += texture2D(map, map_uv + vec2(-0.840144, -0.073580)*sharpness);
    blur += texture2D(map, map_uv + vec2(-0.695914, 0.457137)*sharpness);
    blur += texture2D(map, map_uv + vec2(-0.203345, 0.620716)*sharpness);
    blur += texture2D(map, map_uv + vec2(0.962340, -0.194983)*sharpness);
    blur += texture2D(map, map_uv + vec2(0.473434, -0.480026)*sharpness);
    blur += texture2D(map, map_uv + vec2(0.519456, 0.767022)*sharpness);
    blur += texture2D(map, map_uv + vec2(0.185461, -0.893124)*sharpness);
    blur += texture2D(map, map_uv + vec2(0.507431, 0.064425)*sharpness);
    blur += texture2D(map, map_uv + vec2(0.896420, 0.412458)*sharpness);
    blur += texture2D(map, map_uv + vec2(-0.321940, -0.932615)*sharpness);
    blur += texture2D(map, map_uv + vec2(-0.791559, -0.597705)*sharpness);    
    blur/=12.0;
    blur.a=texture2D(p3d_Texture0, uv).a;     
    blur*=use_map;   
     
    gl_FragColor = brush+blur;    
    //gl_FragColor = color;    
    }
 
