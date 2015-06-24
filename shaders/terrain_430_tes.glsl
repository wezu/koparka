//GLSL
#version 430

layout(triangles, equal_spacing, ccw) in;
in vec3 tcPosition[];
out vec3 tePosition;
out vec3 tePatchDistance;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    vec3 p0 = gl_TessCoord.x * tcPosition[0];
    vec3 p1 = gl_TessCoord.y * tcPosition[1];
    vec3 p2 = gl_TessCoord.z * tcPosition[2];
    tePatchDistance = gl_TessCoord;
    tePosition = (p0 + p1 + p2);
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(tePosition, 1);
}
