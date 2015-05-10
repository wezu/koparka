//GLSL
#version 110

varying vec3 vpos;
//varying float h;

uniform float sunpos;
uniform float osg_FrameTime;
uniform float cloudTile;
uniform float cloudSpeed;

void main()
    { 
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;    
    gl_TexCoord[0] =gl_MultiTexCoord0*cloudTile-osg_FrameTime*cloudSpeed;
    gl_TexCoord[1] =gl_MultiTexCoord0*cloudTile*0.25-osg_FrameTime*cloudSpeed*0.1;  
    gl_TexCoord[3] =gl_MultiTexCoord0*10.0-osg_FrameTime*0.002;    
    gl_TexCoord[2] =gl_MultiTexCoord0+vec4(0.0,sunpos,0.0, 0.0);    
    vpos=gl_Vertex.xyz;    
    }
    