export default class GaussianSplashBackground {
    private canvas: HTMLCanvasElement | null;
    private gl: WebGLRenderingContext | null;
    private program: WebGLProgram | null;
    private centers: number[][];
    private velocities: number[][];
    private colors: number[][];
    private sizes: number[];
    private rainbowColors: string[];
    private numSplashes: number;
    private positionAttributeLocation: number | null;
    private resolutionUniformLocation: WebGLUniformLocation | null;
    private centerUniformLocation: WebGLUniformLocation | null;
    private colorUniformLocation: WebGLUniformLocation | null;
    private sizeUniformLocation: WebGLUniformLocation | null;
    private positionBuffer: WebGLBuffer | null;
    private animationFrameId: number | null;

    constructor() {
        this.canvas = null;
        this.gl = null;
        this.program = null;
        this.centers = [];
        this.velocities = [];
        this.colors = [];
        this.sizes = [];
        this.rainbowColors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3'];
        this.numSplashes = 10;

        this.positionAttributeLocation = null;
        this.resolutionUniformLocation = null;
        this.centerUniformLocation = null;
        this.colorUniformLocation = null;
        this.sizeUniformLocation = null;
        this.positionBuffer = null;
        this.animationFrameId = null;

        this.initCanvas();
        this.initWebGL();
        this.initShaders();
        this.generateSplashes();
        this.setupEventListeners();
        this.render();
    }

    private initCanvas(): void {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'gaussian-splash-background';
        document.body.appendChild(this.canvas);

        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.zIndex = '-1';

        this.resizeCanvas();
    }

    private resizeCanvas(): void {
        if (this.canvas) {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }
        if (this.gl) {
            this.gl.viewport(0, 0, this.canvas!.width, this.canvas!.height);
        }
    }

    private initWebGL(): void {
        if (this.canvas) {
            this.gl = this.canvas.getContext('webgl');
        }
        if (!this.gl) {
            console.error('WebGL not supported');
            return;
        }
        this.gl.clearColor(0, 0, 0, 1);
    }

    private initShaders(): void {
        const vertexShaderSource = `
        attribute vec2 a_position;
        void main() {
            gl_Position = vec4(a_position, 0, 1);
        }`;

        const fragmentShaderSource = `
        precision mediump float;
        uniform vec2 u_resolution;
        uniform vec2 u_center[10];
        uniform vec3 u_color[10];
        uniform float u_size[10];

        float gaussian(float x, float sigma) {
            return exp(-pow(x, 2.0) / (2.0 * pow(sigma, 2.0)));
        }

        void main() {
            vec2 st = gl_FragCoord.xy / u_resolution;
            vec3 color = vec3(0.0);

            for (int i = 0; i < 10; i++) {
                vec2 uv = st - u_center[i];
                float dist = length(uv);

                float splash = gaussian(dist, u_size[i]);
                vec3 splashColor = u_color[i];

                color += splashColor * splash;
            }

            gl_FragColor = vec4(color, 1.0);
        }`;

        const vertexShader = this.createShader(this.gl!.VERTEX_SHADER, vertexShaderSource);
        const fragmentShader = this.createShader(this.gl!.FRAGMENT_SHADER, fragmentShaderSource);
        this.program = this.createProgram(vertexShader!, fragmentShader!);

        this.positionAttributeLocation = this.gl!.getAttribLocation(this.program!, 'a_position');
        this.resolutionUniformLocation = this.gl!.getUniformLocation(this.program!, 'u_resolution');
        this.centerUniformLocation = this.gl!.getUniformLocation(this.program!, 'u_center');
        this.colorUniformLocation = this.gl!.getUniformLocation(this.program!, 'u_color');
        this.sizeUniformLocation = this.gl!.getUniformLocation(this.program!, 'u_size');

        this.positionBuffer = this.gl!.createBuffer();
        this.gl!.bindBuffer(this.gl!.ARRAY_BUFFER, this.positionBuffer);
        const positions = [-1, -1, 1, -1, -1, 1, 1, 1];
        this.gl!.bufferData(this.gl!.ARRAY_BUFFER, new Float32Array(positions), this.gl!.STATIC_DRAW);

        this.gl!.bindBuffer(this.gl!.ARRAY_BUFFER, this.positionBuffer);
        this.gl!.enableVertexAttribArray(this.positionAttributeLocation);
        this.gl!.vertexAttribPointer(this.positionAttributeLocation, 2, this.gl!.FLOAT, false, 0, 0);

        this.gl!.useProgram(this.program);
    }

    private createShader(type: number, source: string): WebGLShader | null {
        const shader = this.gl!.createShader(type);
        this.gl!.shaderSource(shader!, source);
        this.gl!.compileShader(shader!);
        if (!this.gl!.getShaderParameter(shader!, this.gl!.COMPILE_STATUS)) {
            console.error(this.gl!.getShaderInfoLog(shader!));
            this.gl!.deleteShader(shader!);
            return null;
        }
        return shader!;
    }

    private createProgram(vertexShader: WebGLShader, fragmentShader: WebGLShader): WebGLProgram | null {
        const program = this.gl!.createProgram();
        this.gl!.attachShader(program, vertexShader);
        this.gl!.attachShader(program, fragmentShader);
        this.gl!.linkProgram(program);
        if (!this.gl!.getProgramParameter(program, this.gl!.LINK_STATUS)) {
            console.error(this.gl!.getProgramInfoLog(program));
            this.gl!.deleteProgram(program);
            return null;
        }
        return program;
    }

    private generateSplashes(): void {
        for (let i = 0; i < this.numSplashes; i++) {
            this.centers.push([Math.random(), Math.random()]);
            this.velocities.push([(Math.random() - 0.5) * 0.01, (Math.random() - 0.5) * 0.01]);
            const randomColor = this.hexToVec3(this.rainbowColors[Math.floor(Math.random() * this.rainbowColors.length)]);
            this.colors.push(randomColor);
            this.sizes.push(Math.random() * 0.1 + 0.05);
        }
    }

    private hexToVec3(hex: string): number[] {
        const bigint = parseInt(hex.slice(1), 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;
        return [r / 255, g / 255, b / 255];
    }

    private updateCenters(): void {
        for (let i = 0; i < this.centers.length; i++) {
            this.centers[i][0] += this.velocities[i][0];
            this.centers[i][1] += this.velocities[i][1];

            if (this.centers[i][0] < 0 || this.centers[i][0] > 1) this.velocities[i][0] *= -1;
            if (this.centers[i][1] < 0 || this.centers[i][1] > 1) this.velocities[i][1] *= -1;
        }
    }

    private render(): void {
        this.updateCenters();

        this.gl!.clear(this.gl!.COLOR_BUFFER_BIT);

        this.gl!.uniform2f(this.resolutionUniformLocation!, this.canvas!.width, this.canvas!.height);
        this.gl!.uniform2fv(this.centerUniformLocation!, this.centers.flat());
        this.gl!.uniform3fv(this.colorUniformLocation!, this.colors.flat());
        this.gl!.uniform1fv(this.sizeUniformLocation!, this.sizes);

        this.gl!.drawArrays(this.gl!.TRIANGLE_STRIP, 0, 4);

        this.animationFrameId = requestAnimationFrame(this.render.bind(this));
    }

    private setupEventListeners(): void {
        window.addEventListener('resize', this.resizeCanvas.bind(this));
    }

    public cleanup(): void {
        if (this.animationFrameId) cancelAnimationFrame(this.animationFrameId);
        this.canvas!.remove();
        window.removeEventListener('resize', this.resizeCanvas.bind(this));
    }
}
