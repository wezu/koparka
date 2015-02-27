//GLSL
#version 110
uniform sampler2D colortex;
uniform sampler2D shadow_map;
uniform sampler2D auxTex;

void main() 
    {
    vec2 uv=gl_TexCoord[0].xy;
    vec4 color=texture2D(colortex,uv);
    float shadow=texture2D(shadow_map,uv).g*0.8+0.2; 
    float fogfactor=texture2D(auxTex, uv).r;
    
    vec4 blur=texture2D(colortex, uv);
    float sharpness=0.002;
    //Hardcoded fast gaussian blur
    blur += texture2D(colortex, uv + vec2( -0.326212, -0.405805)*sharpness);
    blur += texture2D(colortex, uv + vec2(-0.840144, -0.073580)*sharpness);
    blur += texture2D(colortex, uv + vec2(-0.695914, 0.457137)*sharpness);
    blur += texture2D(colortex, uv + vec2(-0.203345, 0.620716)*sharpness);
    blur += texture2D(colortex, uv + vec2(0.962340, -0.194983)*sharpness);
    blur += texture2D(colortex, uv + vec2(0.473434, -0.480026)*sharpness);
    blur += texture2D(colortex, uv + vec2(0.519456, 0.767022)*sharpness);
    blur += texture2D(colortex, uv + vec2(0.185461, -0.893124)*sharpness);
    blur += texture2D(colortex, uv + vec2(0.507431, 0.064425)*sharpness);
    blur += texture2D(colortex, uv + vec2(0.896420, 0.412458)*sharpness);
    blur += texture2D(colortex, uv + vec2(-0.321940, -0.932615)*sharpness);
    blur += texture2D(colortex, uv + vec2(-0.791559, -0.597705)*sharpness);
    blur /=13.0;      
    color*=shadow;   
    gl_FragColor =mix(color, blur, fogfactor);
    //gl_FragColor =color;
    }