//GLSL
#version 110
varying float blend;
varying vec3 vpos;
//varying float h;

uniform float time;
uniform float horizont;
uniform float cloudTile;
uniform float cloudSpeed;

void main()
    { 
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;    
    gl_TexCoord[0] =gl_MultiTexCoord0*cloudTile-time*cloudSpeed;
    gl_TexCoord[1] =gl_MultiTexCoord0*cloudTile*0.5-time*cloudSpeed*0.5;   
    gl_TexCoord[2] =gl_MultiTexCoord0+vec4(0.0, time*0.01, 0.0, 0.0);
    //blend=clamp((gl_Vertex.z-horizont)/horizont, 0.0, 1.0);
    //h=clamp((gl_Vertex.z-(horizont*0.5))/(horizont*0.5), 0.0, 1.0);
    vpos=gl_Vertex.xyz;
    //color=mix(fog, sky, h);
    }