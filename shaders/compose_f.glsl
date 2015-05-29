//GLSL
#version 110
uniform sampler2D colorTex;
uniform sampler2D blurTex;
uniform sampler2D blurTex2;
uniform sampler2D auxTex;
uniform sampler2D noiseTex;
uniform sampler2D glareTex;
uniform sampler2D flareTex;

void main() 
    {
    vec2 uv=gl_TexCoord[0].xy;    
    vec2 time_uv=gl_TexCoord[1].xy;
    
    vec4 blured_aux=texture2D(blurTex,uv);
    vec4 blured_color=texture2D(blurTex2, uv);
    float shadow=blured_aux.g*0.4+0.6;
    
    vec4 aux=texture2D(auxTex, uv);
    float fogfactor=aux.r;    
    float specfactor=aux.b+blured_aux.b;
    float distor=clamp(aux.a-0.5, 0.0, 0.5)*2.0;  
    
    vec2 noise=texture2D(noiseTex,time_uv).rg*2.0 - 1.0;    
    vec4 color=texture2D(colorTex,uv+noise*0.01*distor);    
    //color+=texture2D(colorTex,uv)*(1.0-distor);
    //color+=blured_color*0.2;
    color*=shadow;
    color=mix(color, blured_color, fogfactor);
    //vec4 color=vec4(0.0, 0.0, 0.0, 0.0);
    color+=texture2D(glareTex,uv);  
    color+=texture2D(flareTex,uv);     
    
    gl_FragColor =color;
    }
