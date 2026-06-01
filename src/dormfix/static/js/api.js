const API_BASE_URL = '/api';
const API_TIMEOUT = 15000; // 15秒超时

const api = {
    /**
     * 发送网络请求的通用封装方法
     * @param {string} url - 接口相对路径 (例如 '/accounts/login/')
     * @param {object} options - Fetch 的配置参数
     */
    async request(url, options = {}) {
        const token = sessionStorage.getItem('dormfix_token');
        const headers = options.headers || {};

        // 1. 自动携带 Token 认证信息
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }

        // 2. 自动处理 Content-Type。如果使用了 FormData（上传图片），不设置由浏览器自动处理 boundary
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }

        options.headers = headers;

        // 3. 添加超时控制
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
        options.signal = controller.signal;

        try {
            const response = await fetch(`${API_BASE_URL}${url}`, options);
            clearTimeout(timeoutId);

            // 4. 拦截 401 状态（认证过期或无效），强制重定向回登录页面
            if (response.status === 401) {
                sessionStorage.removeItem('dormfix_token');
                sessionStorage.removeItem('dormfix_user');
                // 仅在非登录页面时执行跳转，防止死循环
                if (!window.location.pathname.endsWith('/login/')) {
                    window.location.href = '/login/';
                }
                throw new Error('认证已过期，请重新登录');
            }

            // 5. 处理 204 No Content 或空响应
            if (response.status === 204) {
                return null;
            }

            // 6. 如果响应状态码不为 2xx，则抛出后端返回的错误负载
            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    errorData = { detail: `服务器错误 (${response.status})` };
                }
                throw errorData;
            }

            // 7. 对导出报表接口进行特殊文件流接收处理
            if (url.includes('/dashboard/export/')) {
                return await response.blob();
            }

            const responseData = await response.json();
            return responseData;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请检查网络连接后重试');
            }
            console.error('API Error details:', error);
            throw error;
        }
    },
    
    /**
     * 发送 GET 请求
     */
    get(url, options = {}) {
        return this.request(url, { ...options, method: 'GET' });
    },
    
    /**
     * 发送 POST 请求
     */
    post(url, data, options = {}) {
        const body = data instanceof FormData ? data : JSON.stringify(data);
        return this.request(url, { ...options, method: 'POST', body });
    },
    
    /**
     * 发送 PUT 请求
     */
    put(url, data, options = {}) {
        const body = data instanceof FormData ? data : JSON.stringify(data);
        return this.request(url, { ...options, method: 'PUT', body });
    }
};

// 导出 api 实例
window.api = api;
