//GLSL
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

out vec4 color;
out vec2 uv;
out vec2 map_uv;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;     
    color=p3d_Color;
    uv=p3d_MultiTexCoord0;
    vec4 w_pos=p3d_ModelMatrix * p3d_Vertex;   
    map_uv=w_pos.xy/512.0;
    }
