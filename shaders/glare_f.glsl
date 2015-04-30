//GLSL
#version 110
uniform sampler2D auxTex;
uniform sampler2D colorTex;
uniform sampler2D blurTex;

varying vec2 uv;

void main() 
    {        
    vec4 blured_aux=texture2D(blurTex,uv);
    vec4 aux=texture2D(auxTex, uv);  
    float specfactor=aux.b+blured_aux.b;
    
    vec4 color=texture2D(colorTex, uv);   
    
    gl_FragColor =color*specfactor;
    }
 