# Deployment Guide: Vercel (Frontend) + Render (Backend)

## Quick Deployment Steps

### 1. Deploy Backend to Render

1. **Create Render Account**: Go to [render.com](https://render.com) and sign up
2. **Connect GitHub**: Link your GitHub repository
3. **Create Web Service**:
   - Choose your repository
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Root Directory: `backend`
   
4. **Set Environment Variables** in Render dashboard:
   ```
   DEBUG=false
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

5. **Deploy**: Render will automatically deploy your backend
6. **Copy Backend URL**: Save the URL (e.g., `https://your-backend.onrender.com`)

### 2. Deploy Frontend to Vercel

1. **Create Vercel Account**: Go to [vercel.com](https://vercel.com) and sign up
2. **Connect GitHub**: Link your GitHub repository
3. **Import Project**: 
   - Choose your repository
   - Framework: Vite
   - Root Directory: `.` (root)
   
4. **Set Environment Variables** in Vercel dashboard:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api/v1
   VITE_GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

5. **Deploy**: Vercel will automatically build and deploy

### 3. Update CORS in Backend

After getting your Vercel URL, update the backend CORS settings:

1. In Render dashboard, update `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-actual-frontend.vercel.app,https://marine-data-platform.vercel.app
   ```

2. Redeploy the backend service

## Environment Variables Required

### Backend (Render):
- `DEBUG=false`
- `GEMINI_API_KEY=your_google_gemini_api_key`
- `ALLOWED_ORIGINS=https://your-frontend.vercel.app`

### Frontend (Vercel):
- `VITE_API_URL=https://your-backend.onrender.com/api/v1`
- `VITE_GEMINI_API_KEY=your_google_gemini_api_key`

## Testing the Deployment

1. **Backend Health Check**: 
   - Visit: `https://your-backend.onrender.com/health`
   - Should return: `{"status": "healthy", "message": "Marine Data Platform API is running"}`

2. **Frontend**: 
   - Visit your Vercel URL
   - Dashboard should load without 404 errors
   - API Test page should successfully connect to backend

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Update `ALLOWED_ORIGINS` in Render with exact Vercel URLs
2. **404 API Errors**: Check `VITE_API_URL` matches your Render backend URL
3. **Build Failures**: Ensure all dependencies are in package.json and requirements.txt

### Debug Steps:

1. Check Render deployment logs
2. Check Vercel function logs
3. Test backend endpoints directly
4. Verify environment variables are set correctly

## Current Status

✅ **Code Updated**: API configuration works with environment variables
✅ **Backend Fixed**: CORS configured for Vercel domains  
✅ **AI Analysis**: Real OBIS occurrence data integration complete
✅ **Deployment Ready**: Configuration files created

## Next Steps

1. Push code to GitHub
2. Deploy backend to Render
3. Deploy frontend to Vercel
4. Set environment variables
5. Test the live application

The application will have:
- 🌊 Real OBIS marine data integration
- 🤖 AI analysis with actual species occurrence records
- 📊 Interactive charts and visualizations
- 🚀 Production-ready deployment