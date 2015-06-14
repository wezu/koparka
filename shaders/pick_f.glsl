//GLSL
#version 110

varying vec2 wpos;

void main()
    { 
    //pack the x and y wpos into rgba    
    vec4 final= vec4(wpos.x, wpos.y, 1.0, 1.0);
    gl_FragData[0] =final;
    }
    
