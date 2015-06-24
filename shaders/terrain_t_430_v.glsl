//GLSL
#version 430

in vec4 p3d_Vertex;
out vec3 controlpoint_wor;

void main()
    {
    controlpoint_wor = p3d_Vertex.xyz;
    }
