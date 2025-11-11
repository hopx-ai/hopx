/**
 * Template Builder - Fluent API for building templates
 */

import { Step, StepType, CopyOptions, ReadyCheck, BuildOptions, BuildResult, RegistryAuth, GCPRegistryAuth, AWSRegistryAuth } from './types.js';
import { buildTemplate } from './build-flow.js';
import * as fs from 'fs';
import * as path from 'path';

export class Template {
  private steps: Step[] = [];
  private startCmd?: string;
  private readyCheck?: ReadyCheck;
  
  /**
   * Create a new template builder
   */
  constructor() {}
  
  // ==================== Base Images ====================
  
  /**
   * Start from Ubuntu base image
   */
  fromUbuntuImage(version: string): Template {
    this.steps.push({
      type: StepType.FROM,
      args: [`ubuntu:${version}`],
    });
    return this;
  }
  
  /**
   * Start from Python base image
   */
  fromPythonImage(version: string): Template {
    this.steps.push({
      type: StepType.FROM,
      args: [`python:${version}`],
    });
    return this;
  }
  
  /**
   * Start from Node.js base image
   */
  fromNodeImage(version: string): Template {
    this.steps.push({
      type: StepType.FROM,
      args: [`node:${version}`],
    });
    return this;
  }
  
  /**
   * Start from any Docker image (with optional authentication)
   */
  fromImage(image: string, auth?: RegistryAuth): Template {
    this.steps.push({
      type: StepType.FROM,
      args: [image],
      registryAuth: auth,
    });
    return this;
  }
  
  /**
   * Start from GCP Container Registry image
   */
  fromGCPRegistry(image: string, auth: GCPRegistryAuth): Template {
    let serviceAccount: any;
    
    if (typeof auth.serviceAccountJSON === 'string') {
      // It's a file path
      const filePath = path.resolve(auth.serviceAccountJSON);
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      serviceAccount = JSON.parse(fileContent);
    } else {
      // It's already an object
      serviceAccount = auth.serviceAccountJSON;
    }
    
    // GCP uses _json_key as username and full JSON as password
    const registryAuth: RegistryAuth = {
      username: '_json_key',
      password: JSON.stringify(serviceAccount),
    };
    
    return this.fromImage(image, registryAuth);
  }
  
  /**
   * Start from AWS ECR image
   */
  fromAWSRegistry(image: string, auth: AWSRegistryAuth): Template {
    // Store AWS credentials - backend will handle token exchange
    this.steps.push({
      type: StepType.FROM,
      args: [image],
      awsAuth: auth,
    });
    return this;
  }
  
  // ==================== File Operations ====================
  
  /**
   * Copy files to the template
   */
  copy(src: string | string[], dest: string, options?: CopyOptions): Template {
    const sources = Array.isArray(src) ? src : [src];
    
    this.steps.push({
      type: StepType.COPY,
      args: [sources.join(','), dest, JSON.stringify(options || {})],
      // filesHash will be calculated during build
    });
    return this;
  }
  
  // ==================== Commands ====================
  
  /**
   * Run a command during build
   */
  runCmd(cmd: string): Template {
    this.steps.push({
      type: StepType.RUN,
      args: [cmd],
    });
    return this;
  }
  
  // ==================== Environment ====================
  
  /**
   * Set an environment variable
   */
  setEnv(key: string, value: string): Template {
    this.steps.push({
      type: StepType.ENV,
      args: [key, value],
    });
    return this;
  }
  
  /**
   * Set multiple environment variables
   */
  setEnvs(vars: Record<string, string>): Template {
    for (const [key, value] of Object.entries(vars)) {
      this.setEnv(key, value);
    }
    return this;
  }
  
  // ==================== Working Directory ====================
  
  /**
   * Set working directory
   */
  setWorkdir(dir: string): Template {
    this.steps.push({
      type: StepType.WORKDIR,
      args: [dir],
    });
    return this;
  }
  
  // ==================== User ====================
  
  /**
   * Set user
   */
  setUser(user: string): Template {
    this.steps.push({
      type: StepType.USER,
      args: [user],
    });
    return this;
  }
  
  // ==================== Smart Helpers ====================
  
  /**
   * Install packages with apt
   * 
   * @example
   * .aptInstall('curl', 'git', 'vim')  // Multiple args
   * .aptInstall(['curl', 'git', 'vim'])  // Array
   * .aptInstall('curl').aptInstall('git')  // Chained
   */
  aptInstall(...packages: (string | string[])[]): Template {
    // Flatten arguments
    const pkgList: string[] = [];
    for (const pkg of packages) {
      if (Array.isArray(pkg)) {
        pkgList.push(...pkg);
      } else {
        pkgList.push(pkg);
      }
    }
    
    if (pkgList.length === 0) {
      throw new Error('aptInstall requires at least one package');
    }
    
    const pkgs = pkgList.join(' ');
    this.runCmd(`apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y ${pkgs}`);
    return this;
  }
  
  /**
   * Install Python packages with pip
   * 
   * @example
   * .pipInstall('numpy', 'pandas')  // Multiple args
   * .pipInstall(['numpy', 'pandas'])  // Array
   * .pipInstall('numpy').pipInstall('pandas')  // Chained
   * .pipInstall()  // Install from requirements.txt
   */
  pipInstall(...packages: (string | string[])[]): Template {
    // Handle no args (requirements.txt)
    if (packages.length === 0) {
      this.runCmd('/usr/local/bin/pip3 install --no-cache-dir -r requirements.txt');
      return this;
    }
    
    // Flatten arguments
    const pkgList: string[] = [];
    for (const pkg of packages) {
      if (Array.isArray(pkg)) {
        pkgList.push(...pkg);
      } else {
        pkgList.push(pkg);
      }
    }
    
    if (pkgList.length === 0) {
      throw new Error('pipInstall requires at least one package or no args for requirements.txt');
    }
    
    const pkgs = pkgList.join(' ');
    // Use full path for pip (works after systemd restart)
    this.runCmd(`/usr/local/bin/pip3 install --no-cache-dir ${pkgs}`);
    return this;
  }
  
  /**
   * Install Node packages with npm
   * 
   * @example
   * .npmInstall('typescript', 'tsx')  // Multiple args
   * .npmInstall(['typescript', 'tsx'])  // Array
   * .npmInstall('typescript').npmInstall('tsx')  // Chained
   * .npmInstall()  // Install from package.json
   */
  npmInstall(...packages: (string | string[])[]): Template {
    // Handle no args (package.json)
    if (packages.length === 0) {
      this.runCmd('/usr/bin/npm install');
      return this;
    }
    
    // Flatten arguments
    const pkgList: string[] = [];
    for (const pkg of packages) {
      if (Array.isArray(pkg)) {
        pkgList.push(...pkg);
      } else {
        pkgList.push(pkg);
      }
    }
    
    if (pkgList.length === 0) {
      throw new Error('npmInstall requires at least one package or no args for package.json');
    }
    
    const pkgs = pkgList.join(' ');
    // Use full path for npm (works after systemd restart)
    this.runCmd(`/usr/bin/npm install -g ${pkgs}`);
    return this;
  }
  
  /**
   * Install Go packages
   */
  goInstall(packages: string[]): Template {
    for (const pkg of packages) {
      this.runCmd(`go install ${pkg}`);
    }
    return this;
  }
  
  /**
   * Install Rust packages with cargo
   */
  cargoInstall(packages: string[]): Template {
    for (const pkg of packages) {
      this.runCmd(`cargo install ${pkg}`);
    }
    return this;
  }
  
  /**
   * Clone a git repository
   */
  gitClone(url: string, dest: string): Template {
    this.runCmd(`git clone ${url} ${dest}`);
    return this;
  }
  
  // ==================== Caching ====================
  
  /**
   * Skip cache for this step
   */
  skipCache(): Template {
    if (this.steps.length > 0) {
      this.steps[this.steps.length - 1].skipCache = true;
    }
    return this;
  }
  
  // ==================== Start Command ====================
  
  /**
   * Set the start command and ready check
   */
  setStartCmd(cmd: string, ready?: ReadyCheck): Template {
    this.startCmd = cmd;
    this.readyCheck = ready;
    return this;
  }
  
  // ==================== Build ====================
  
  /**
   * Get all steps
   */
  getSteps(): Step[] {
    return this.steps;
  }
  
  /**
   * Get start command
   */
  getStartCmd(): string | undefined {
    return this.startCmd;
  }
  
  /**
   * Get ready check
   */
  getReadyCheck(): ReadyCheck | undefined {
    return this.readyCheck;
  }
  
  /**
   * Build the template
   */
  static async build(template: Template, options: BuildOptions): Promise<BuildResult> {
    return buildTemplate(template, options);
  }
}

// Factory function
export function createTemplate(): Template {
  return new Template();
}

