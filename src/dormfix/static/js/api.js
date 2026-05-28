const API_BASE_URL = '/api';

const api = {
    /**
     * 发送网络请求的通用封装方法
     * @param {string} url - 接口相对路径 (例如 '/accounts/login/')
     * @param {object} options - Fetch 的配置参数
     */
    async request(url, options = {}) {
        const token = localStorage.getItem('dormfix_token');
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

        try {
            const response = await fetch(`${API_BASE_URL}${url}`, options);
            
            // 3. 拦截 401 状态（认证过期或无效），强制重定向回登录页面
            if (response.status === 401) {
                localStorage.removeItem('dormfix_token');
                localStorage.removeItem('dormfix_user');
                // 仅在非登录页面时执行跳转，防止死循环
                if (!window.location.pathname.endsWith('/login/')) {
                    window.location.href = '/login/';
                }
                return;
            }
            
            // 4. 处理 204 No Content 或空响应
            if (response.status === 204) {
                return null;
            }
            
            // 5. 对导出报表接口进行特殊文件流接收处理
            if (url.includes('/dashboard/export/')) {
                return await response.blob();
            }

            const responseData = await response.json();
            
            // 6. 如果响应状态码不为 2xx，则抛出后端返回的错误负载
            if (!response.ok) {
                throw responseData;
            }
            return responseData;
        } catch (error) {
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
