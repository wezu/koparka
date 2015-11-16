//GLSL
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec3 vpos;
out vec2 uv0;
out vec2 uv1;
out vec2 uv2;
out vec2 uv3;

uniform float sunpos;
uniform float osg_FrameTime;
uniform float cloudTile;
uniform float cloudSpeed;

void main()
    { 
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;    
    uv0 =p3d_MultiTexCoord0*cloudTile-osg_FrameTime*cloudSpeed;
    uv1 =p3d_MultiTexCoord0*cloudTile*0.25-osg_FrameTime*cloudSpeed*0.1;  
    uv2 =p3d_MultiTexCoord0+vec2(0.0,sunpos);
    uv3 =p3d_MultiTexCoord0*10.0-osg_FrameTime*0.002;            
    vpos=p3d_Vertex.xyz;    
    }
    
