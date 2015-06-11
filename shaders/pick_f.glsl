//GLSL
#version 110

varying vec2 uv;


void main()
    { 
    //pack the x and y wpos into rgba    
    vec4 final= vec4(uv.x ,fract(uv.x*256.0),uv.y ,fract(uv.y*256.0));
    gl_FragData[0] =final;
    gl_FragData[1] =vec4(0.0, 1.0, 0.0,0.0);
    }
    
