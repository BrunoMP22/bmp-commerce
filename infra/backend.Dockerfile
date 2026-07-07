FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

COPY backend/BMPCommerce.sln ./
COPY backend/src/BMPCommerce.Domain/BMPCommerce.Domain.csproj src/BMPCommerce.Domain/
COPY backend/src/BMPCommerce.Application/BMPCommerce.Application.csproj src/BMPCommerce.Application/
COPY backend/src/BMPCommerce.Infrastructure/BMPCommerce.Infrastructure.csproj src/BMPCommerce.Infrastructure/
COPY backend/src/BMPCommerce.API/BMPCommerce.API.csproj src/BMPCommerce.API/
RUN dotnet restore src/BMPCommerce.API/BMPCommerce.API.csproj

COPY backend/src/ src/
RUN dotnet publish src/BMPCommerce.API/BMPCommerce.API.csproj -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app
COPY --from=build /app ./

ENTRYPOINT ["dotnet", "BMPCommerce.API.dll"]
